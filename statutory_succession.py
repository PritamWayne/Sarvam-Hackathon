"""
Statutory Succession Rules Engine for Indian Inheritance Jurisprudence.
Implements:
- Hindu Succession Act, 1956 (HSA) - Section 6, 8, 9, 10, 14
- Hindu Succession (Amendment) Act, 2005 (equal coparcenary rights for daughters)
- Supreme Court precedent: Vineeta Sharma v. Rakesh Sharma (2020) 9 SCC 1
- Per stirpes branch representation for predeceased heirs
- Exact rational fraction computation (fractions.Fraction)
"""

from fractions import Fraction
from typing import List, Dict, Any, Optional, Set, Tuple
from schema import VanshavaliTree, PersonNode, RelationshipEdge
from title_audit_models import StatutoryHeirShare


class StatutorySuccessionEngine:
    """
    Computes theoretical lawful inheritance shares for family tree members
    based on statutory succession acts and judicial precedents.
    """

    def __init__(
        self,
        governing_law: str = "HSA_1956_AMENDED_2005",
        is_agricultural_land: bool = True
    ):
        self.governing_law = governing_law
        self.is_agricultural_land = is_agricultural_land

    def compute_succession_shares(
        self,
        vanshavali: VanshavaliTree,
        total_plot_area_sq_m: float
    ) -> List[StatutoryHeirShare]:
        """
        Computes statutory shares across generations from ancestral head down to claimant.
        Returns a list of StatutoryHeirShare objects for each living descendant / heir.
        """
        # Build quick adjacency and lookup maps
        members_by_id: Dict[str, PersonNode] = {m.person_id: m for m in vanshavali.members}
        head = vanshavali.ancestral_head
        if head.person_id not in members_by_id:
            members_by_id[head.person_id] = head

        children_of: Dict[str, List[str]] = {}
        spouses_of: Dict[str, List[str]] = {}
        parents_of: Dict[str, List[str]] = {}

        for rel in vanshavali.relationships:
            if rel.relation_type == "parent_of":
                children_of.setdefault(rel.source_id, []).append(rel.target_id)
                parents_of.setdefault(rel.target_id, []).append(rel.source_id)
            elif rel.relation_type == "child_of":
                children_of.setdefault(rel.target_id, []).append(rel.source_id)
                parents_of.setdefault(rel.source_id, []).append(rel.target_id)
            elif rel.relation_type == "spouse_of":
                spouses_of.setdefault(rel.source_id, []).append(rel.target_id)
                spouses_of.setdefault(rel.target_id, []).append(rel.source_id)

        # Trace devolution from root ancestral head
        # We recursively devolve shares branch by branch
        shares_map: Dict[str, Fraction] = {head.person_id: Fraction(1, 1)}

        # Breadth-first traversal down generations
        queue = [head.person_id]
        processed_devolutions: Set[str] = set()

        while queue:
            current_id = queue.pop(0)
            current_person = members_by_id.get(current_id)
            if not current_person or current_id in processed_devolutions:
                continue

            current_share = shares_map.get(current_id, Fraction(0, 1))
            if current_share == 0:
                continue

            # If person is deceased, their share devolves upon their Class I heirs
            if current_person.status == "deceased":
                heir_shares = self._devolve_estate_of_deceased(
                    deceased_id=current_id,
                    current_estate_fraction=current_share,
                    members_by_id=members_by_id,
                    children_of=children_of,
                    spouses_of=spouses_of
                )
                
                # Person's personal holding is now fully distributed
                shares_map[current_id] = Fraction(0, 1)

                # Apply devolved shares to heirs
                for heir_id, share in heir_shares.items():
                    shares_map[heir_id] = shares_map.get(heir_id, Fraction(0, 1)) + share
                    if heir_id not in queue and members_by_id.get(heir_id):
                        # If heir is also deceased, add to queue so their share devolves further
                        if members_by_id[heir_id].status == "deceased":
                            queue.append(heir_id)

                processed_devolutions.add(current_id)

        # Formulate StatutoryHeirShare models for all living members and key claimant branches
        results: List[StatutoryHeirShare] = []
        for pid, member in members_by_id.items():
            # If member is deceased and had descendants who took their share, show 0 or mark devolved
            frac = shares_map.get(pid, Fraction(0, 1))
            frac_val = float(frac)
            entitled_area_sq_m = frac_val * total_plot_area_sq_m
            entitled_area_acres = entitled_area_sq_m / 4046.8564224

            rel_desc = self._describe_relationship(member, head, parents_of, spouses_of, members_by_id)

            status = "Entitled" if frac > 0 else ("Devolved to Heirs" if member.status == "deceased" else "No Direct Share")

            results.append(
                StatutoryHeirShare(
                    person_id=member.person_id,
                    name=member.name,
                    relationship_to_deceased=rel_desc,
                    heir_class="Class I Legal Heir" if member.generation_level <= 2 else "Branch Successor",
                    statutory_fraction_str=str(frac),
                    statutory_fraction_val=round(frac_val, 6),
                    theoretical_area_sq_m=round(entitled_area_sq_m, 2),
                    theoretical_area_acres=round(entitled_area_acres, 4),
                    recorded_share_fraction_str=None,
                    recorded_share_fraction_val=0.0,
                    recorded_area_sq_m=0.0,
                    deprived_fraction_str=str(frac) if member.is_claimant else None,
                    deprived_area_sq_m=round(entitled_area_sq_m, 2) if member.is_claimant else 0.0,
                    is_claimant=member.is_claimant,
                    status=status
                )
            )

        return results

    def _devolve_estate_of_deceased(
        self,
        deceased_id: str,
        current_estate_fraction: Fraction,
        members_by_id: Dict[str, PersonNode],
        children_of: Dict[str, List[str]],
        spouses_of: Dict[str, List[str]]
    ) -> Dict[str, Fraction]:
        """
        Applies HSA Sec 8 & 10 (and post-2005 Sec 6 rules):
        Class I Heirs take simultaneously and in equal shares per capita / per stirpes:
        - Surviving Widow(s) (1 share)
        - Surviving Sons / Daughters / Child branches (1 share each)
        """
        all_children = children_of.get(deceased_id, [])
        all_spouses = spouses_of.get(deceased_id, [])

        surviving_widows = [
            s_id for s_id in all_spouses 
            if members_by_id.get(s_id) and members_by_id[s_id].status == "alive"
        ]

        # Each child or child's branch represents 1 unit
        # Even if a child is deceased, that child's branch takes 1 share (which will then devolve to their heirs)
        valid_children = [c_id for c_id in all_children if members_by_id.get(c_id)]

        total_units = len(valid_children) + (1 if surviving_widows else 0)

        if total_units == 0:
            return {}

        unit_share = current_estate_fraction / Fraction(total_units, 1)
        result: Dict[str, Fraction] = {}

        # Devolve to widows
        if surviving_widows:
            widow_share = unit_share / Fraction(len(surviving_widows), 1)
            for w_id in surviving_widows:
                result[w_id] = widow_share

        # Devolve to children branches
        for child_id in valid_children:
            result[child_id] = unit_share

        return result

    def _describe_relationship(
        self,
        member: PersonNode,
        head: PersonNode,
        parents_of: Dict[str, List[str]],
        spouses_of: Dict[str, List[str]],
        members_by_id: Dict[str, PersonNode]
    ) -> str:
        if member.person_id == head.person_id:
            return "Ancestral Patriarch / Original Titleholder"

        parents = parents_of.get(member.person_id, [])
        if parents:
            p_names = [members_by_id[p].name for p in parents if p in members_by_id]
            parent_str = f" of {', '.join(p_names)}" if p_names else ""
            if member.gender == "female":
                return f"Daughter{parent_str}"
            elif member.gender == "male":
                return f"Son{parent_str}"
            return f"Child{parent_str}"

        spouses = spouses_of.get(member.person_id, [])
        if spouses:
            s_names = [members_by_id[s].name for s in spouses if s in members_by_id]
            return f"Widow / Spouse of {', '.join(s_names)}"

        return f"Legal Heir (Gen {member.generation_level})"

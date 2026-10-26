# Sarvam AI & Indus Web Companion Guide

**Platform URL:** [https://indus.sarvam.ai/](https://indus.sarvam.ai/)

This file provides copy-paste prompts and API payloads to interact directly with Sarvam AI's Indus LLM and Bulbul TTS web platform.

## 1. Bulbul TTS Web Voice Briefing Prompt
Copy and paste the text below into the Sarvam AI Bulbul Audio Playground:

```text
प्रणाम हरिशंकर मिश्रा (Harishankar Mishra) जी। हम आपकी पैतृक भूमि मौजा चक-गोविंदपुर, तहसील मवाना, मेरठ के संबंध में राजस्व एवं कानूनी जांच रिपोर्ट लेकर उपस्थित हुए हैं। हम भली-भांति समझते हैं कि जब अपने ही परिवार के सदस्य छल से पुश्तैनी हक़ छीनने का प्रयास करते हैं, तो कितनी मानसिक वेदना होती है। परंतु आप बिल्कुल निश्चिंत रहें, सारे दस्तावेज़ और कानून पूरी तरह आपके पक्ष में हैं।

हमारी जांच में यह स्पष्ट सिद्ध हुआ है कि आपके बाबा स्वर्गीय रामेश्वर मिश्रा (Rameshwar Mishra) जी के पास कुल 12 बीघा (12 Bigha) जमीन थी। वर्ष 1988 के चकबंदी बंटवारे के अनुसार आपके पिता स्वर्गीय भोलानाथ मिश्रा (Bholanath Mishra) जी का वैध हिस्सा 6 बीघा (6 Bigha / 50% अंश) निर्धारित हुआ था। पिता जी के उपरांत आप तीनों भाइयों—हरिशंकर, उमाशंकर और रविशंकर—का प्रत्येक का हिस्सा 2 बीघा (2 Bigha प्रत्येक भाई) बनता है।

परंतु डिजिटल खतौनी के समय आपके चचेरे भाई कमलेश मिश्रा (Kamlesh Mishra) ने बिना किसी सार्वजनिक मुनादी या कानूनी सूचना के, हल्का पटवारी की मिलीभगत से खसरा संख्या 142 और 143 की कुल 4 बीघा पक्की जमीन (4 Bigha) ज़मीन अपने नाम फर्जी वरासत करा ली। हमारे गणितीय ऑडिट ने यह साबित किया है कि कमलेश मिश्रा (Kamlesh Mishra) के खाते में 4.0 बीघा, यानी लगभग 10,117 वर्ग मीटर का अवैध अधिशेष दर्ज है, जो प्राकृतिक न्याय के विरुद्ध है।

इस अन्याय के निवारण हेतु हमने तहसीलदार / उप-जिलाधिकारी, मवाना न्यायालय के समक्ष उत्तर प्रदेश राजस्व संहिता की धारा 34 व 35 के तहत एक अत्यंत सुदृढ़ कानूनी आपत्ति याचिका तैयार कर ली है। इसमें आपकी वंशावली, 1988 का चकबंदी रिकॉर्ड, और गणितीय ऑडिट रिपोर्ट संलग्न है। यह याचिका डाउनलोड हेतु तैयार है, जिस पर केवल आपके हस्ताक्षर होने हैं। न्याय आपके साथ है।
```

**Recommended Voice Settings:**
- **Model:** `bulbul:v3`
- **Language:** Hindi (`hi-IN`)
- **Speaker:** `aditya_hi_conversational` (or `amit_hi_conversational`)
- **Pace:** 1.0
- **Pitch:** 0.0
- **Format:** WAV / MP3 (44.1 kHz)

## 2. Indus LLM Revenue Extraction Prompt
```text
You are Indus Land Records Intelligence, an expert in Indian Revenue Systems, Jamabandi, Khatauni, RoR, and Land Survey settlement records across all Indian states.
Your task is to extract land plot information and co-sharer (Hissedari) breakdown from given record extracts.

Output MUST be valid JSON with the following structure:
{
  "state": "State name (e.g. Uttar Pradesh, Punjab, Maharashtra)",
  "district": "District name",
  "tehsil": "Tehsil or Taluka name",
  "plot_id": "Khasra / Khewat / Survey number",
  "total_registered_area": "Raw total registered area (e.g. '3 Bigha 10 Biswa', '5-12 Kanal-Marla', '2.5 Hectare')",
  "unit_hint": "Dominant unit (e.g. bigha, kanal, hectare, cent)",
  "co_sharers": [
    {
      "name": "Co-sharer / Hissedar name with parentage if available",
      "share": "Fractional share (e.g. '1/3', '4 Annas', '25%') OR recorded parcel area if given as specific area",
      "recorded_area": "Optional explicit parcel area string if stated separately"
    }
  ]
}


Revenue Record Excerpt to Audit:
ग्राम: चक-गोविंदपुर, तहसील: मवाना, जनपद: मेरठ (उत्तर प्रदेश)
खाता संख्या: 00112, खसरा संख्या: 142 एवं 143
कुल दर्ज रकबा: 4 बीघा 0 बिस्वा (पुख्ता)
दर्ज खातेदार: कमलेश मिश्रा पुत्र स्वर्गीय दीनानाथ मिश्रा
आपत्तिकर्तागण: हरिशंकर मिश्रा, उमाशंकर मिश्रा, रविशंकर मिश्रा पुत्रगण स्वर्गीय भोलानाथ मिश्रा
पैतृक हिस्सा: 6 बीघा (50% कुल 12 बीघा में से)
```

## 3. Python API Invocation Snippet (Bulbul TTS)
```python
import os
from sarvamai import SarvamAI

client = SarvamAI(api_subscription_key=os.getenv('SARVAM_API_KEY'))
response = client.text_to_speech.convert(
    text='प्रणाम हरिशंकर मिश्रा (Harishankar Mishra) जी। हम आपकी पैतृक भूमि मौजा चक-गोविंदपुर, तहसील मवाना, मे...',
    language_code='hi-IN',
    model='bulbul:v3',
    speaker='aditya_hi_conversational',
    output_audio_codec='wav'
)
with open('landholder_audio.wav', 'wb') as f:
    f.write(response.audios[0].encode('utf-8'))
```

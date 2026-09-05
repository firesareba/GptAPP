import 'dart:convert';
import 'package:http/http.dart' as http;
import 'api_client.dart';
import 'secure_keys.dart';

class LlmClient {
  LlmClient({required this.provider, required this.model, required this.apiKey});
  final String provider, model, apiKey;

  Future<Map<String,dynamic>> generateAndSubmit({required ApiClient api,required String userId,int? materialId,required String material,required String topic,required double difficulty,int? battleId}) async {
    final instruction='Create one original practice problem based only on the supplied study material. Paraphrase; never copy source wording. Return JSON only with keys prompt, answer, type, explanation. type must be multiple_choice, numeric, or short_answer. Difficulty target: $difficulty. Topic: $topic. Material:\n$material';
    final text=await _complete(instruction);
    Map<String,dynamic>? raw;
    try { final decoded=jsonDecode(text); if(decoded is! Map) throw const FormatException('Invalid problem JSON'); raw=Map<String,dynamic>.from(decoded); if(!{'prompt','answer','type'}.every(raw!.containsKey)) throw const FormatException('Invalid problem JSON'); return await api.submitGeneration(userId:userId,materialId:materialId,topic:topic,difficulty:difficulty,rawResponse:raw,battleId:battleId); }
    finally { raw=null; }
  }

  Future<String> _complete(String prompt) async {
    switch(provider){case 'openai':return _openAi(prompt);case 'anthropic':return _anthropic(prompt);case 'gemini':return _gemini(prompt);default:throw UnsupportedError('Unsupported LLM provider: $provider');}
  }
  Future<String> _openAi(String prompt) async { final r=await http.post(Uri.parse('https://api.openai.com/v1/responses'),headers:{'Authorization':'Bearer $apiKey','Content-Type':'application/json','Cache-Control':'no-store'},body:jsonEncode({'model':model,'input':prompt})); _check(r); final j=jsonDecode(r.body); return (j['output'] as List).expand((x)=>(x['content'] as List)).map((x)=>x['text']??'').join(); }
  Future<String> _anthropic(String prompt) async { final r=await http.post(Uri.parse('https://api.anthropic.com/v1/messages'),headers:{'x-api-key':apiKey,'anthropic-version':'2023-06-01','Content-Type':'application/json','Cache-Control':'no-store'},body:jsonEncode({'model':model,'max_tokens':1200,'messages':[{'role':'user','content':prompt}]})); _check(r); final j=jsonDecode(r.body); return (j['content'] as List).map((x)=>x['text']??'').join(); }
  Future<String> _gemini(String prompt) async { final r=await http.post(Uri.parse('https://generativelanguage.googleapis.com/v1beta/models/$model:generateContent?key=$apiKey'),headers:{'Content-Type':'application/json','Cache-Control':'no-store'},body:jsonEncode({'contents':[{'parts':[{'text':prompt}]}]})); _check(r); final j=jsonDecode(r.body); return j['candidates'][0]['content']['parts'][0]['text'] as String; }
  void _check(http.Response r){if(r.statusCode<200||r.statusCode>=300)throw Exception('LLM request failed: ${r.statusCode}');}
}

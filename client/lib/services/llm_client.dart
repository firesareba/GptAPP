import 'dart:convert';
import 'package:http/http.dart' as http;

class LlmClient {
  LlmClient({required this.provider, required this.model, required this.apiKey});
  final String provider, model, apiKey;

  Future<Map<String,dynamic>> generateProblem({required String material, required String topic, required double difficulty}) async {
    final instruction = '''Create one original practice problem based only on the supplied study material. Paraphrase; never copy source wording. Return JSON only with keys: prompt, answer, type, explanation. type must be multiple_choice, numeric, or short_answer. Difficulty target: $difficulty. Topic: $topic. Material:\n$material''';
    final text = await _complete(instruction);
    final value = jsonDecode(text);
    if (value is! Map<String,dynamic> || !{'prompt','answer','type'}.every(value.containsKey)) throw FormatException('Invalid problem JSON');
    return value;
  }

  Future<Map<String,dynamic>> grade({required int problemId, required String prompt, required String expectedAnswer, required String submittedAnswer}) async {
    final instruction = '''Grade this student's answer. Return JSON only: {"problem_id":$problemId,"submitted_answer":<exact submitted answer>,"correct":true|false,"reason":"brief reason"}. Do not reveal the expected answer in reason. Problem: $prompt\nReference answer: $expectedAnswer\nStudent answer: $submittedAnswer''';
    final text = await _complete(instruction);
    final value = jsonDecode(text);
    if (value is! Map<String,dynamic> || value['problem_id'] != problemId || value['submitted_answer'] != submittedAnswer || value['correct'] is! bool) throw FormatException('Invalid grading JSON');
    return value;
  }

  Future<String> _complete(String prompt) async {
    switch (provider) {
      case 'openai': return _openAi(prompt);
      case 'anthropic': return _anthropic(prompt);
      case 'gemini': return _gemini(prompt);
      default: throw UnsupportedError('Unsupported LLM provider: $provider');
    }
  }

  Future<String> _openAi(String prompt) async {
    final r = await http.post(Uri.parse('https://api.openai.com/v1/responses'), headers: {'Authorization':'Bearer $apiKey','Content-Type':'application/json'}, body: jsonEncode({'model':model,'input':prompt}));
    _check(r); final j=jsonDecode(r.body); return (j['output'] as List).expand((x)=>(x['content'] as List)).map((x)=>x['text'] ?? '').join();
  }
  Future<String> _anthropic(String prompt) async {
    final r = await http.post(Uri.parse('https://api.anthropic.com/v1/messages'), headers: {'x-api-key':apiKey,'anthropic-version':'2023-06-01','Content-Type':'application/json'}, body: jsonEncode({'model':model,'max_tokens':1200,'messages':[{'role':'user','content':prompt}]}));
    _check(r); final j=jsonDecode(r.body); return (j['content'] as List).map((x)=>x['text'] ?? '').join();
  }
  Future<String> _gemini(String prompt) async {
    final r = await http.post(Uri.parse('https://generativelanguage.googleapis.com/v1beta/models/$model:generateContent?key=$apiKey'), headers: {'Content-Type':'application/json'}, body: jsonEncode({'contents':[{'parts':[{'text':prompt}]}]}));
    _check(r); final j=jsonDecode(r.body); return j['candidates'][0]['content']['parts'][0]['text'] as String;
  }
  void _check(http.Response r) { if (r.statusCode < 200 || r.statusCode >= 300) throw Exception('LLM request failed: ${r.statusCode}'); }
}

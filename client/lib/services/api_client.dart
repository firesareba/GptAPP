import 'dart:convert';
import 'dart:typed_data';
import 'package:http/http.dart' as http;

class ApiClient {
  ApiClient(this.baseUrl); final String baseUrl;
  Future<Map<String,dynamic>> uploadText(String userId,String text) async { final u=Uri.parse('$baseUrl/materials/text').replace(queryParameters:{'user_id':userId,'text':text}); return _json(await http.post(u)); }
  Future<Map<String,dynamic>> uploadPdf(String userId,String filename,Uint8List bytes) async { final q=http.MultipartRequest('POST',Uri.parse('$baseUrl/materials/pdf'))..fields['user_id']=userId..files.add(http.MultipartFile.fromBytes('file',bytes,filename:filename)); return _json(await http.Response.fromStream(await q.send())); }
  Future<Map<String,dynamic>> submitGeneration({required String userId,int? materialId,required String topic,required double difficulty,required Map<String,dynamic> rawResponse}) async { final r=await http.post(Uri.parse('$baseUrl/problems/generation'),headers:{'content-type':'application/json'},body:jsonEncode({'user_id':userId,'material_id':materialId,'topic':topic,'difficulty':difficulty,'raw_llm_response':rawResponse})); return _json(r); }
  Future<Map<String,dynamic>> recordAttempt({required String userId,required int problemId,required String answer,required int elapsedMs}) async { final r=await http.post(Uri.parse('$baseUrl/attempts'),headers:{'content-type':'application/json'},body:jsonEncode({'user_id':userId,'problem_id':problemId,'submitted_answer':answer,'elapsed_ms':elapsedMs})); return _json(r); }
  Map<String,dynamic> _json(http.Response r){ if(r.statusCode<200||r.statusCode>=300) throw Exception(r.body); return jsonDecode(r.body) as Map<String,dynamic>; }
}

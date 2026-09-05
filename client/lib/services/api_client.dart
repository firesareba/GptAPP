import 'dart:convert';
import 'dart:typed_data';
import 'package:http/http.dart' as http;
class ApiClient {
 ApiClient(this.baseUrl); final String baseUrl;
 Map<String,String> get _headers=>{'content-type':'application/json','cache-control':'no-store','pragma':'no-cache'};
 Future<Map<String,dynamic>> uploadText(String userId,String text)async=>_json(await http.post(Uri.parse('$baseUrl/materials/text').replace(queryParameters:{'user_id':userId,'text':text}),headers:_headers));
 Future<Map<String,dynamic>> uploadPdf(String userId,String filename,Uint8List bytes)async{final q=http.MultipartRequest('POST',Uri.parse('$baseUrl/materials/pdf'))..headers.addAll({'cache-control':'no-store','pragma':'no-cache'})..fields['user_id']=userId..files.add(http.MultipartFile.fromBytes('file',bytes,filename:filename));return _json(await http.Response.fromStream(await q.send()));}
 Future<Map<String,dynamic>> submitGeneration({required String userId,int? materialId,required String topic,required double difficulty,required Map<String,dynamic> rawResponse,int? battleId})async=>_json(await http.post(Uri.parse('$baseUrl/problems/generation'),headers:_headers,body:jsonEncode({'user_id':userId,'material_id':materialId,'topic':topic,'difficulty':difficulty,'raw_llm_response':rawResponse,'battle_id':battleId})));
 Future<Map<String,dynamic>> recordAttempt({required String userId,required int problemId,required String answer,required int elapsedMs,int? battleId})async=>_json(await http.post(Uri.parse('$baseUrl/attempts'),headers:_headers,body:jsonEncode({'user_id':userId,'problem_id':problemId,'submitted_answer':answer,'elapsed_ms':elapsedMs,'battle_id':battleId})));
 Future<List<dynamic>> topics(String userId)async{final r=await http.get(Uri.parse('$baseUrl/topics').replace(queryParameters:{'user_id':userId}),headers:_headers);if(r.statusCode<200||r.statusCode>=300)throw Exception('Request failed: ${r.statusCode}');return jsonDecode(r.body) as List<dynamic>;}
 Future<double> wallet(String userId)async{final j=_json(await http.get(Uri.parse('$baseUrl/wallet').replace(queryParameters:{'user_id':userId}),headers:_headers));return (j['balance'] as num).toDouble();}
 Future<Map<String,dynamic>> startBoss(String userId,int topicId)async=>_json(await http.post(Uri.parse('$baseUrl/boss/start').replace(queryParameters:{'user_id':userId,'topic_id':'$topicId'}),headers:_headers));
 Future<Map<String,dynamic>> boss(int battleId,String userId)async=>_json(await http.get(Uri.parse('$baseUrl/boss/$battleId').replace(queryParameters:{'user_id':userId}),headers:_headers));
 Future<List<dynamic>> cosmetics(String userId)async{final r=await http.get(Uri.parse('$baseUrl/cosmetics').replace(queryParameters:{'user_id':userId}),headers:_headers);if(r.statusCode<200||r.statusCode>=300)throw Exception('Request failed: ${r.statusCode}');return jsonDecode(r.body) as List<dynamic>;}
 Future<Map<String,dynamic>> buyCosmetic(int id,String userId)async=>_json(await http.post(Uri.parse('$baseUrl/cosmetics/$id/buy').replace(queryParameters:{'user_id':userId}),headers:_headers));
 Map<String,dynamic> _json(http.Response r){if(r.statusCode<200||r.statusCode>=300)throw Exception('Request failed: ${r.statusCode}');return jsonDecode(r.body) as Map<String,dynamic>;}
}

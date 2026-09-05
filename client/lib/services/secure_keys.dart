import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class SecureKeys {
  static const _storage = FlutterSecureStorage();
  static const _llmApiKey = 'llm_api_key';

  static Future<void> saveLlmApiKey(String key) => _storage.write(key: _llmApiKey, value: key);
  static Future<String?> readLlmApiKey() => _storage.read(key: _llmApiKey);
  static Future<void> clearLlmApiKey() => _storage.delete(key: _llmApiKey);
}

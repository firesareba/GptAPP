import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class SecureKeys {
  static const _storage = FlutterSecureStorage();
  static String _key(String provider) => 'llm_api_key_$provider';
  static Future<void> saveLlmApiKey(String provider, String key) => _storage.write(key: _key(provider), value: key);
  static Future<String?> readLlmApiKey(String provider) => _storage.read(key: _key(provider));
  static Future<void> clearLlmApiKey(String provider) => _storage.delete(key: _key(provider));
}

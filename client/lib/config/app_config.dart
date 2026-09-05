import 'package:flutter/services.dart' show rootBundle;
import 'package:yaml/yaml.dart';

class AppConfig {
  AppConfig._(this._data);
  final YamlMap _data;
  static Future<AppConfig> load() async {
    final raw = await rootBundle.loadString('assets/config.yaml');
    return AppConfig._(loadYaml(raw) as YamlMap);
  }
  String get name => _data['app']['name'] as String;
  String get currencyName => _data['app']['currency_name'] as String;
  String get backendBaseUrl => _data['backend']['base_url'] as String;
  String get primaryColor => _data['branding']['primary_color'] as String;
  String modelFor(String provider) => _data['llm']['default_models'][provider] as String;
}

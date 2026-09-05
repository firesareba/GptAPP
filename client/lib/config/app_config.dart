import 'package:flutter/services.dart' show rootBundle;
import 'package:yaml/yaml.dart';

class AppConfig {
  AppConfig._(this._data);
  final YamlMap _data;
  static Future<AppConfig> load() async { final raw=await rootBundle.loadString('assets/config.yaml'); return AppConfig._(loadYaml(raw) as YamlMap); }
  String get name=>_data['app']['name'] as String;
  String get currencyName=>_data['app']['currency_name'] as String;
  String get backendBaseUrl=>_data['backend']['base_url'] as String;
  String get primaryColor=>_data['branding']['primary_color'] as String;
  List<String> get providers=>List<String>.from((_data['llm']['providers'] as YamlList).map((x)=>x.toString()));
  String modelFor(String provider)=>_data['llm']['default_models'][provider] as String;
  double get targetMinAccuracy=>(_data['difficulty']['target_min_accuracy'] as num).toDouble();
  double get targetMaxAccuracy=>(_data['difficulty']['target_max_accuracy'] as num).toDouble();
  int get bossTimePerTurn=>(_data['boss_battle']['default_time_per_turn_seconds'] as num).toInt();
  String get quietStart=>_data['nudge']['quiet_start'] as String;
  String get quietEnd=>_data['nudge']['quiet_end'] as String;
}

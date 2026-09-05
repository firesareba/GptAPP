import 'package:flutter/material.dart';
import 'config/app_config.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  final config = await AppConfig.load();
  runApp(GptApp(config: config));
}

class GptApp extends StatelessWidget {
  const GptApp({super.key, required this.config});
  final AppConfig config;
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: config.name,
      debugShowCheckedModeBanner: false,
      theme: ThemeData(colorSchemeSeed: _color(config.primaryColor), useMaterial3: true),
      home: HomePage(config: config),
    );
  }
}

Color _color(String value) {
  final hex = value.replaceFirst('#', '');
  return Color(int.parse(hex.length == 6 ? 'FF$hex' : hex, radix: 16));
}

class HomePage extends StatefulWidget {
  const HomePage({super.key, required this.config});
  final AppConfig config;
  @override State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  int tab = 0;
  final List<String> materials = [];
  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: Text(widget.config.name), actions: [IconButton(onPressed: () => _showKey(context), icon: const Icon(Icons.key_outlined))]),
    body: IndexedStack(index: tab, children: [_Dashboard(materials: materials, currency: widget.config.currencyName), _MaterialPage(onAdded: (name) => setState(() => materials.add(name))), const _PracticePage()]),
    bottomNavigationBar: NavigationBar(selectedIndex: tab, onDestinationSelected: (v) => setState(() => tab = v), destinations: const [
      NavigationDestination(icon: Icon(Icons.home_outlined), selectedIcon: Icon(Icons.home), label: 'Home'),
      NavigationDestination(icon: Icon(Icons.library_books_outlined), selectedIcon: Icon(Icons.library_books), label: 'Materials'),
      NavigationDestination(icon: Icon(Icons.quiz_outlined), selectedIcon: Icon(Icons.quiz), label: 'Practice'),
    ]),
  );

  void _showKey(BuildContext context) => showDialog(context: context, builder: (_) => const _KeyDialog());
}

class _KeyDialog extends StatefulWidget { const _KeyDialog(); @override State<_KeyDialog> createState() => _KeyDialogState(); }
class _KeyDialogState extends State<_KeyDialog> {
  final controller = TextEditingController();
  @override Widget build(BuildContext context) => AlertDialog(title: const Text('LLM API key'), content: TextField(controller: controller, obscureText: true, decoration: const InputDecoration(hintText: 'Stored only in platform secure storage')), actions: [TextButton(onPressed: () => Navigator.pop(context), child: const Text('Cancel')), FilledButton(onPressed: () => Navigator.pop(context), child: const Text('Save'))]);
}

class _Dashboard extends StatelessWidget {
  const _Dashboard({required this.materials, required this.currency});
  final List<String> materials; final String currency;
  @override Widget build(BuildContext context) => ListView(padding: const EdgeInsets.all(20), children: [
    Text('Ready to study?', style: Theme.of(context).textTheme.headlineMedium?.copyWith(fontWeight: FontWeight.bold)),
    const SizedBox(height: 8), const Text('Upload your material, then generate original practice problems from it.'),
    const SizedBox(height: 24), Card(child: Padding(padding: const EdgeInsets.all(20), child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: const [Text('Verified core loop', style: TextStyle(fontWeight: FontWeight.bold)), SizedBox(height: 8), Text('Material → generated problem → submitted answer → permanently recorded attempt.')]))),
    const SizedBox(height: 24), Text(currency, style: Theme.of(context).textTheme.titleLarge),
    const ListTile(leading: Icon(Icons.account_balance_wallet_outlined), title: Text('0'), subtitle: Text('Currency is enabled after Phase 1 verification.')),
    const SizedBox(height: 12), Text('Materials', style: Theme.of(context).textTheme.titleLarge),
    ...materials.map((m) => ListTile(leading: const Icon(Icons.description_outlined), title: Text(m))),
  ]);
}

class _MaterialPage extends StatelessWidget {
  const _MaterialPage({required this.onAdded}); final void Function(String) onAdded;
  @override Widget build(BuildContext context) => Center(child: Padding(padding: const EdgeInsets.all(24), child: Column(mainAxisAlignment: MainAxisAlignment.center, children: [
    const Icon(Icons.upload_file_outlined, size: 64), const SizedBox(height: 16),
    Text('Add study material', style: Theme.of(context).textTheme.headlineSmall), const SizedBox(height: 8),
    const Text('PDFs must contain an extractable text layer. OCR and image input are not supported.', textAlign: TextAlign.center), const SizedBox(height: 24),
    FilledButton.icon(onPressed: () => _paste(context), icon: const Icon(Icons.text_fields), label: const Text('Paste text')),
  ]));
  void _paste(BuildContext context) { final c = TextEditingController(); showDialog(context: context, builder: (_) => AlertDialog(title: const Text('Paste study text'), content: TextField(controller: c, minLines: 5, maxLines: 10, decoration: const InputDecoration(hintText: 'Paste your material here')), actions: [TextButton(onPressed: () => Navigator.pop(context), child: const Text('Cancel')), FilledButton(onPressed: () { if (c.text.trim().isNotEmpty) onAdded('New material'); Navigator.pop(context); }, child: const Text('Add'))])); }
}
class _PracticePage extends StatelessWidget { const _PracticePage(); @override Widget build(BuildContext context) => const Center(child: Text('Generate a problem after adding material.')); }

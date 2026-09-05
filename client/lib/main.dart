import 'package:flutter/material.dart';

void main() => runApp(const GptApp());

class GptApp extends StatelessWidget {
  const GptApp({super.key});
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'GptAPP',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(colorSchemeSeed: const Color(0xFF6750A4), useMaterial3: true),
      home: const HomePage(),
    );
  }
}

class HomePage extends StatefulWidget {
  const HomePage({super.key});
  @override State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  int tab = 0;
  final List<String> topics = ['Get started by adding study material'];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('GptAPP'), actions: [IconButton(onPressed: () {}, icon: const Icon(Icons.settings_outlined))]),
      body: IndexedStack(index: tab, children: [
        _Dashboard(topics: topics),
        _MaterialPage(onAdded: (name) => setState(() => topics.add(name))),
        const _PracticePage(),
      ]),
      bottomNavigationBar: NavigationBar(selectedIndex: tab, onDestinationSelected: (v) => setState(() => tab = v), destinations: const [
        NavigationDestination(icon: Icon(Icons.home_outlined), selectedIcon: Icon(Icons.home), label: 'Home'),
        NavigationDestination(icon: Icon(Icons.library_books_outlined), selectedIcon: Icon(Icons.library_books), label: 'Materials'),
        NavigationDestination(icon: Icon(Icons.quiz_outlined), selectedIcon: Icon(Icons.quiz), label: 'Practice'),
      ]),
    );
  }
}

class _Dashboard extends StatelessWidget {
  const _Dashboard({required this.topics});
  final List<String> topics;
  @override Widget build(BuildContext context) => ListView(padding: const EdgeInsets.all(20), children: [
    Text('Ready to study?', style: Theme.of(context).textTheme.headlineMedium?.copyWith(fontWeight: FontWeight.bold)),
    const SizedBox(height: 8), const Text('Upload your material, then generate original practice problems from it.'),
    const SizedBox(height: 24), Card(child: Padding(padding: const EdgeInsets.all(20), child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: const [Text('Phase 1', style: TextStyle(fontWeight: FontWeight.bold)), SizedBox(height: 8), Text('Verified core loop: material → generated problem → submitted answer → permanently recorded attempt.')]))),
    const SizedBox(height: 24), Text('Topics', style: Theme.of(context).textTheme.titleLarge),
    ...topics.map((t) => ListTile(leading: const Icon(Icons.topic_outlined), title: Text(t))),
  ]);
}

class _MaterialPage extends StatelessWidget {
  const _MaterialPage({required this.onAdded});
  final void Function(String) onAdded;
  @override Widget build(BuildContext context) => Center(child: Padding(padding: const EdgeInsets.all(24), child: Column(mainAxisAlignment: MainAxisAlignment.center, children: [
    const Icon(Icons.upload_file_outlined, size: 64), const SizedBox(height: 16),
    Text('Add study material', style: Theme.of(context).textTheme.headlineSmall), const SizedBox(height: 8),
    const Text('PDFs must contain an extractable text layer. OCR and image input are not supported.', textAlign: TextAlign.center), const SizedBox(height: 24),
    FilledButton.icon(onPressed: () => _paste(context), icon: const Icon(Icons.text_fields), label: const Text('Paste text')),
  ])));
  void _paste(BuildContext context) { final c = TextEditingController(); showDialog(context: context, builder: (_) => AlertDialog(title: const Text('Paste study text'), content: TextField(controller: c, minLines: 5, maxLines: 10, decoration: const InputDecoration(hintText: 'Paste your material here')), actions: [TextButton(onPressed: () => Navigator.pop(context), child: const Text('Cancel')), FilledButton(onPressed: () { if (c.text.trim().isNotEmpty) onAdded('New material'); Navigator.pop(context); }, child: const Text('Add'))])); }
}

class _PracticePage extends StatelessWidget {
  const _PracticePage();
  @override Widget build(BuildContext context) => const Center(child: Text('Generate a problem after adding material.'));
}

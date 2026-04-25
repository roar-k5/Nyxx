import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../services/api_service.dart';
import '../theme/app_colors.dart';
import 'crisis_screen.dart';

class ChatScreen extends StatefulWidget {
  const ChatScreen({super.key});

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final _messageController = TextEditingController();
  final _scrollController = ScrollController();
  final List<Map<String, dynamic>> _messages = [];
  bool _isLoading = false;
  String? _userName;

  @override
  void initState() {
    super.initState();
    _loadUser();
    _messages.add({
      'role': 'assistant',
      'content':
          "Hi, I'm NYX. Tell me what's happening, and we'll take it one step at a time.",
      'emotion': 'neutral',
    });
  }

  Future<void> _loadUser() async {
    final prefs = await SharedPreferences.getInstance();
    final userJson = prefs.getString('user');
    if (userJson != null) {
      final user = jsonDecode(userJson);
      setState(() => _userName = user['name']);
    }
  }

  Future<void> _sendMessage() async {
    final text = _messageController.text.trim();
    if (text.isEmpty) return;

    setState(() {
      _messages.add({'role': 'user', 'content': text});
      _messageController.clear();
      _isLoading = true;
    });
    _scrollToBottom();

    try {
      final apiResponse = await ApiService.sendMessage(
        text,
        history: _messages
            .where((m) => m.containsKey('content'))
            .map((m) => {
                  'role': m['role'],
                  'content': m['content'],
                })
            .toList(),
      );

      if (apiResponse.isCrisis) {
        if (mounted) {
          Navigator.of(context).push(
            MaterialPageRoute(
              builder: (_) => CrisisScreen(
                response: apiResponse,
                onDismiss: () => Navigator.of(context).pop(),
              ),
            ),
          );
        }
        setState(() => _isLoading = false);
        return;
      }

      setState(() {
        _messages.add({
          'role': 'assistant',
          'content': apiResponse.response,
          'emotion': apiResponse.primaryEmotion ?? 'neutral',
          'crisis': apiResponse.crisis,
        });
        _isLoading = false;
      });
      _scrollToBottom();
    } catch (_) {
      setState(() {
        _messages.add({
          'role': 'assistant',
          'content': "I'm having trouble connecting. Please try again.",
        });
        _isLoading = false;
      });
      _scrollToBottom();
    }
  }

  void _scrollToBottom() {
    Future.delayed(const Duration(milliseconds: 100), () {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  Future<void> _logout() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.clear();
    if (!mounted) return;
    Navigator.pushReplacementNamed(context, '/login');
  }

  @override
  Widget build(BuildContext context) {
    final textPrimary = AppColors.textPrimary(context);
    final textSecondary = AppColors.textSecondary(context);
    final border = AppColors.border(context);
    final isDark = AppColors.isDark(context);

    return Scaffold(
      appBar: AppBar(
        title: Row(
          children: [
            Container(
              width: 38,
              height: 38,
              decoration: const BoxDecoration(
                shape: BoxShape.circle,
                gradient: AppColors.primaryGradient,
              ),
              child: const Center(
                child: Text(
                  'N',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                ),
              ),
            ),
            const SizedBox(width: 12),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  _userName == null ? 'NYX Mind' : 'NYX Mind - $_userName',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: textPrimary,
                  ),
                ),
                Text(
                  _isLoading ? 'typing...' : 'soft space, no pressure',
                  style: TextStyle(
                    fontSize: 12,
                    color: textSecondary,
                  ),
                ),
              ],
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.insights, color: AppColors.primary),
            onPressed: () => Navigator.pushNamed(context, '/mood'),
          ),
          IconButton(
            icon: const Icon(Icons.logout, color: AppColors.textSecondary),
            onPressed: _logout,
          ),
        ],
      ),
      body: Container(
        decoration: BoxDecoration(gradient: AppColors.pageGradient(context)),
        child: Column(
          children: [
            Expanded(
              child: ListView.builder(
                controller: _scrollController,
                padding: const EdgeInsets.all(16),
                itemCount: _messages.length,
                itemBuilder: (context, index) {
                  final msg = _messages[index];
                  final isUser = msg['role'] == 'user';
                  final crisis = msg['crisis'] == true;
                  final emotion = msg['emotion'] as String?;

                  return Align(
                    alignment:
                        isUser ? Alignment.centerRight : Alignment.centerLeft,
                    child: Container(
                      margin: const EdgeInsets.only(bottom: 12),
                      padding: const EdgeInsets.symmetric(
                        horizontal: 16,
                        vertical: 12,
                      ),
                      constraints: BoxConstraints(
                        maxWidth: MediaQuery.of(context).size.width * 0.78,
                      ),
                      decoration: BoxDecoration(
                        color: isUser
                            ? AppColors.primary.withValues(
                                alpha: isDark ? 0.24 : 0.16,
                              )
                            : AppColors.surface(context)
                                .withValues(alpha: isDark ? 0.92 : 0.82),
                        borderRadius: BorderRadius.circular(22),
                        border: Border.all(
                          color: crisis
                              ? AppColors.danger.withValues(alpha: 0.4)
                              : border,
                        ),
                        boxShadow: [
                          BoxShadow(
                            color: AppColors.primary.withValues(alpha: 0.08),
                            blurRadius: 16,
                            offset: const Offset(0, 8),
                          ),
                        ],
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            isUser ? 'You' : 'NYX Mind',
                            style: TextStyle(
                              fontSize: 12,
                              fontWeight: FontWeight.bold,
                              color: isUser
                                  ? AppColors.primaryDark
                                  : AppColors.secondary,
                            ),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            msg['content'] ?? '',
                            style: TextStyle(
                              fontSize: 14,
                              color: textPrimary,
                              height: 1.45,
                            ),
                          ),
                          if (emotion != null && !isUser)
                            Padding(
                              padding: const EdgeInsets.only(top: 6),
                              child: Text(
                                'emotion: $emotion',
                                style: TextStyle(
                                  fontSize: 10,
                                  color: textSecondary,
                                ),
                              ),
                            ),
                        ],
                      ),
                    ),
                  );
                },
              ),
            ),
            if (_isLoading)
              Padding(
                padding: const EdgeInsets.only(left: 16, bottom: 8),
                child: Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 12,
                        vertical: 8,
                      ),
                      decoration: BoxDecoration(
                        color: AppColors.surface(context)
                            .withValues(alpha: isDark ? 0.92 : 0.84),
                        borderRadius: BorderRadius.circular(16),
                        border: Border.all(color: border),
                      ),
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          _buildDot(0),
                          _buildDot(1),
                          _buildDot(2),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: AppColors.surface(context)
                    .withValues(alpha: isDark ? 0.85 : 0.7),
                border: Border(
                  top: BorderSide(color: border),
                ),
              ),
              child: SafeArea(
                child: Row(
                  children: [
                    Expanded(
                      child: TextField(
                        controller: _messageController,
                        style: TextStyle(color: textPrimary),
                        decoration: InputDecoration(
                          hintText: 'Share what\'s on your mind...',
                          hintStyle: TextStyle(color: textSecondary),
                          filled: true,
                          fillColor: AppColors.surface(context)
                              .withValues(alpha: isDark ? 0.96 : 0.92),
                          border: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(27),
                            borderSide: BorderSide(color: border),
                          ),
                          contentPadding: const EdgeInsets.symmetric(
                            horizontal: 20,
                            vertical: 14,
                          ),
                        ),
                        onSubmitted: (_) => _sendMessage(),
                      ),
                    ),
                    const SizedBox(width: 8),
                    GestureDetector(
                      onTap: _sendMessage,
                      child: Container(
                        width: 50,
                        height: 50,
                        decoration: const BoxDecoration(
                          shape: BoxShape.circle,
                          gradient: AppColors.primaryGradient,
                        ),
                        child: const Icon(
                          Icons.send,
                          color: Colors.white,
                          size: 22,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildDot(int index) {
    return AnimatedContainer(
      duration: const Duration(milliseconds: 300),
      margin: const EdgeInsets.symmetric(horizontal: 2),
      width: 8,
      height: 8,
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        color: AppColors.primary.withValues(
          alpha:
              0.5 + 0.5 * ((DateTime.now().millisecond / 1000 + index * 0.3) % 1),
        ),
      ),
    );
  }

  @override
  void dispose() {
    _messageController.dispose();
    _scrollController.dispose();
    super.dispose();
  }
}

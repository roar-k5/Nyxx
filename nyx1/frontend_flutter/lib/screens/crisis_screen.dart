import 'package:flutter/material.dart';

import '../services/api_service.dart';

class CrisisScreen extends StatelessWidget {
  final ApiResponse response;
  final VoidCallback onDismiss;

  const CrisisScreen({
    super.key,
    required this.response,
    required this.onDismiss,
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFFFF5F5),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              const SizedBox(height: 40),
              Container(
                width: 80,
                height: 80,
                decoration: BoxDecoration(
                  color: Colors.red.shade100,
                  shape: BoxShape.circle,
                ),
                child: Icon(
                  Icons.favorite,
                  color: Colors.red.shade700,
                  size: 40,
                ),
              ),
              const SizedBox(height: 24),
              Text(
                "I'm Really Concerned",
                style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                      fontWeight: FontWeight.bold,
                      color: Colors.red.shade800,
                    ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 16),
              Text(
                response.crisisMessage ??
                    "I'm really concerned about what you're going through right now.\n\nI'm just an AI companion and not trained to handle crisis situations safely.\n\nPlease get help immediately from a real person.",
                style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                      color: const Color(0xFF3C1F1F),
                      height: 1.5,
                    ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 32),
              Text(
                '24/7 Helplines',
                style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.bold,
                      color: const Color(0xFF3C1F1F),
                    ),
              ),
              const SizedBox(height: 16),
              if (response.helplines != null)
                ...response.helplines!
                    .map((h) => _buildHelplineCard(context, h)),
              const SizedBox(height: 32),
              SizedBox(
                width: double.infinity,
                child: OutlinedButton(
                  onPressed: onDismiss,
                  child: const Text("I'm Okay, Continue Chat"),
                ),
              ),
              const SizedBox(height: 16),
              Text(
                "I'm still here if you want to talk while you reach out for help.\nTake one small step and call someone now.",
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                      color: const Color(0xFF8B6A6A),
                      fontStyle: FontStyle.italic,
                    ),
                textAlign: TextAlign.center,
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildHelplineCard(BuildContext context, CrisisHelpline helpline) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.05),
            blurRadius: 10,
          ),
        ],
      ),
      child: Row(
        children: [
          Container(
            width: 40,
            height: 40,
            decoration: BoxDecoration(
              color: Colors.green.shade50,
              borderRadius: BorderRadius.circular(8),
            ),
            child: Icon(
              helpline.whatsapp ? Icons.chat_bubble : Icons.phone,
              color: Colors.green.shade700,
              size: 20,
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  helpline.name,
                  style: Theme.of(context).textTheme.titleSmall?.copyWith(
                        fontWeight: FontWeight.bold,
                        color: const Color(0xFF3C1F1F),
                      ),
                ),
                Text(
                  helpline.number,
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                        color: const Color(0xFFB3261E),
                        fontWeight: FontWeight.w600,
                      ),
                ),
                Padding(
                  padding: const EdgeInsets.only(top: 4),
                  child: Text(
                    [
                      helpline.available,
                      if ((helpline.languages ?? '').isNotEmpty)
                        helpline.languages!,
                    ].join(' • '),
                    style: Theme.of(context).textTheme.bodySmall?.copyWith(
                          color: const Color(0xFF8B6A6A),
                        ),
                  ),
                ),
              ],
            ),
          ),
          const Icon(
            Icons.arrow_forward_ios,
            size: 14,
            color: Color(0xFF8B6A6A),
          ),
        ],
      ),
    );
  }
}

import 'package:flutter/material.dart';

import '../services/api_service.dart';
import '../theme/app_colors.dart';

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
    final textPrimary = AppColors.textPrimary(context);
    final textSecondary = AppColors.textSecondary(context);
    final border = AppColors.border(context);

    return Scaffold(
      body: Container(
        decoration: BoxDecoration(gradient: AppColors.pageGradient(context)),
        child: SafeArea(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(24),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.center,
              children: [
                const SizedBox(height: 20),
                Container(
                  width: 88,
                  height: 88,
                  decoration: BoxDecoration(
                    gradient: const LinearGradient(
                      colors: [Color(0xFFFF8A8A), Color(0xFFFFB86C)],
                    ),
                    shape: BoxShape.circle,
                    boxShadow: [
                      BoxShadow(
                        color: AppColors.danger.withValues(alpha: 0.2),
                        blurRadius: 24,
                        offset: const Offset(0, 10),
                      ),
                    ],
                  ),
                  child: const Icon(
                    Icons.favorite_rounded,
                    color: Colors.white,
                    size: 42,
                  ),
                ),
                const SizedBox(height: 24),
                Container(
                  width: double.infinity,
                  padding: const EdgeInsets.all(24),
                  decoration: BoxDecoration(
                    gradient: AppColors.panelGradient(context),
                    borderRadius: BorderRadius.circular(28),
                    border: Border.all(color: border),
                  ),
                  child: Column(
                    children: [
                      Text(
                        "I'm Really Concerned",
                        style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                              fontWeight: FontWeight.bold,
                              color: AppColors.danger,
                            ),
                        textAlign: TextAlign.center,
                      ),
                      const SizedBox(height: 16),
                      Text(
                        response.crisisMessage ??
                            "I'm really concerned about what you're going through right now.\n\nI'm just an AI companion and not trained to handle crisis situations safely.\n\nPlease get help immediately from a real person.",
                        style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                              color: textPrimary,
                              height: 1.55,
                            ),
                        textAlign: TextAlign.center,
                      ),
                      const SizedBox(height: 20),
                      Container(
                        width: double.infinity,
                        padding: const EdgeInsets.all(14),
                        decoration: BoxDecoration(
                          color: AppColors.danger.withValues(alpha: 0.1),
                          borderRadius: BorderRadius.circular(18),
                          border: Border.all(
                            color: AppColors.danger.withValues(alpha: 0.18),
                          ),
                        ),
                        child: Text(
                          'Please contact a trusted person or helpline right now.',
                          style: TextStyle(
                            color: textPrimary,
                            fontWeight: FontWeight.w600,
                          ),
                          textAlign: TextAlign.center,
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 24),
                Align(
                  alignment: Alignment.centerLeft,
                  child: Text(
                    '24/7 Helplines',
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.bold,
                          color: textPrimary,
                        ),
                  ),
                ),
                const SizedBox(height: 14),
                if (response.helplines != null)
                  ...response.helplines!.map((h) => _buildHelplineCard(
                        context,
                        h,
                        textPrimary,
                        textSecondary,
                        border,
                      )),
                const SizedBox(height: 24),
                SizedBox(
                  width: double.infinity,
                  child: OutlinedButton(
                    onPressed: onDismiss,
                    style: OutlinedButton.styleFrom(
                      padding: const EdgeInsets.symmetric(vertical: 16),
                      side: BorderSide(color: border),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(22),
                      ),
                    ),
                    child: const Text("I'm Okay, Continue Chat"),
                  ),
                ),
                const SizedBox(height: 16),
                Text(
                  "I'm still here if you want to talk while you reach out for help.\nTake one small step and call someone now.",
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        color: textSecondary,
                        fontStyle: FontStyle.italic,
                      ),
                  textAlign: TextAlign.center,
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildHelplineCard(
    BuildContext context,
    CrisisHelpline helpline,
    Color textPrimary,
    Color textSecondary,
    Color border,
  ) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: AppColors.panelGradient(context),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: border),
        boxShadow: [
          BoxShadow(
            color: AppColors.primary.withValues(alpha: 0.08),
            blurRadius: 14,
            offset: const Offset(0, 8),
          ),
        ],
      ),
      child: Row(
        children: [
          Container(
            width: 44,
            height: 44,
            decoration: BoxDecoration(
              color: AppColors.success.withValues(alpha: 0.14),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Icon(
              helpline.whatsapp ? Icons.chat_bubble_rounded : Icons.call_rounded,
              color: AppColors.success,
              size: 22,
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
                        color: textPrimary,
                      ),
                ),
                Text(
                  helpline.number,
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                        color: AppColors.danger,
                        fontWeight: FontWeight.w700,
                      ),
                ),
                Padding(
                  padding: const EdgeInsets.only(top: 4),
                  child: Text(
                    [
                      helpline.available,
                      if ((helpline.languages ?? '').isNotEmpty)
                        helpline.languages!,
                    ].join(' - '),
                    style: Theme.of(context).textTheme.bodySmall?.copyWith(
                          color: textSecondary,
                        ),
                  ),
                ),
              ],
            ),
          ),
          Icon(
            Icons.arrow_forward_ios_rounded,
            size: 14,
            color: textSecondary,
          ),
        ],
      ),
    );
  }
}

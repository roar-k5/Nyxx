import 'package:flutter/material.dart';

class AppColors {
  static const Color lightBackgroundTop = Color(0xFFFFF7ED);
  static const Color lightBackgroundMiddle = Color(0xFFFFE4E6);
  static const Color lightBackgroundBottom = Color(0xFFE0F2FE);
  static const Color lightSurface = Color(0xFFFFFFFF);
  static const Color lightSurfaceSoft = Color(0xFFFFFBFF);
  static const Color lightBorder = Color(0xFFF1D3E0);
  static const Color lightTextPrimary = Color(0xFF2D1B38);
  static const Color lightTextSecondary = Color(0xFF7A5A6A);

  static const Color darkBackgroundTop = Color(0xFF140F1F);
  static const Color darkBackgroundMiddle = Color(0xFF1E1530);
  static const Color darkBackgroundBottom = Color(0xFF0F2433);
  static const Color darkSurface = Color(0xFF241A33);
  static const Color darkSurfaceSoft = Color(0xFF2B213B);
  static const Color darkBorder = Color(0xFF443255);
  static const Color darkTextPrimary = Color(0xFFF8EEF7);
  static const Color darkTextSecondary = Color(0xFFC9B4C6);

  static const Color primary = Color(0xFFFF6B8A);
  static const Color primaryDark = Color(0xFFE64980);
  static const Color secondary = Color(0xFF38BDF8);
  static const Color accent = Color(0xFFFFB86C);

  static const Color success = Color(0xFF22C55E);
  static const Color warning = Color(0xFFF59E0B);
  static const Color danger = Color(0xFFEF4444);

  static bool isDark(BuildContext context) =>
      Theme.of(context).brightness == Brightness.dark;

  static Color backgroundTop(BuildContext context) =>
      isDark(context) ? darkBackgroundTop : lightBackgroundTop;

  static Color backgroundMiddle(BuildContext context) =>
      isDark(context) ? darkBackgroundMiddle : lightBackgroundMiddle;

  static Color backgroundBottom(BuildContext context) =>
      isDark(context) ? darkBackgroundBottom : lightBackgroundBottom;

  static Color surface(BuildContext context) =>
      isDark(context) ? darkSurface : lightSurface;

  static Color surfaceSoft(BuildContext context) =>
      isDark(context) ? darkSurfaceSoft : lightSurfaceSoft;

  static Color border(BuildContext context) =>
      isDark(context) ? darkBorder : lightBorder;

  static Color textPrimary(BuildContext context) =>
      isDark(context) ? darkTextPrimary : lightTextPrimary;

  static Color textSecondary(BuildContext context) =>
      isDark(context) ? darkTextSecondary : lightTextSecondary;

  static LinearGradient pageGradient(BuildContext context) => LinearGradient(
        begin: Alignment.topLeft,
        end: Alignment.bottomRight,
        colors: [
          backgroundTop(context),
          backgroundMiddle(context),
          backgroundBottom(context),
        ],
      );

  static LinearGradient panelGradient(BuildContext context) => LinearGradient(
        begin: Alignment.topLeft,
        end: Alignment.bottomRight,
        colors: [
          surface(context).withValues(alpha: isDark(context) ? 0.94 : 0.9),
          surfaceSoft(context),
        ],
      );

  static const LinearGradient primaryGradient = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [primary, accent],
  );

  static LinearGradient coolGradient(BuildContext context) => isDark(context)
      ? const LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [Color(0xFF2A1E3A), Color(0xFF20182D), Color(0xFF173042)],
        )
      : const LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [Color(0xFFFFF9F2), Color(0xFFFDF2F8), Color(0xFFE0F2FE)],
        );
}

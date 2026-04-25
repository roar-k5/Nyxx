import 'package:flutter/material.dart';
import 'screens/splash_screen.dart';
import 'screens/login_screen.dart';
import 'screens/register_screen.dart';
import 'screens/chat_screen.dart';
import 'screens/mood_dashboard.dart';
import 'theme/app_colors.dart';

void main() {
  runApp(const NYXApp());
}

class NYXApp extends StatelessWidget {
  const NYXApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'NYX Mind',
      debugShowCheckedModeBanner: false,
      themeMode: ThemeMode.system,
      theme: ThemeData(
        useMaterial3: true,
        fontFamily: 'Georgia',
        brightness: Brightness.light,
        scaffoldBackgroundColor: AppColors.lightBackgroundTop,
        primaryColor: AppColors.primary,
        colorScheme: const ColorScheme.light(
          primary: AppColors.primary,
          secondary: AppColors.secondary,
          surface: AppColors.lightSurface,
          error: AppColors.danger,
          onPrimary: Colors.white,
          onSecondary: Colors.white,
          onSurface: AppColors.lightTextPrimary,
          onError: Colors.white,
        ),
        appBarTheme: const AppBarTheme(
          backgroundColor: Colors.transparent,
          foregroundColor: AppColors.lightTextPrimary,
          elevation: 0,
          centerTitle: false,
        ),
        cardColor: AppColors.lightSurface,
        textTheme: const TextTheme(
          headlineMedium: TextStyle(
            color: AppColors.lightTextPrimary,
            fontWeight: FontWeight.w700,
          ),
          bodyLarge: TextStyle(
            color: AppColors.lightTextPrimary,
          ),
          bodyMedium: TextStyle(
            color: AppColors.lightTextSecondary,
          ),
        ),
        inputDecorationTheme: InputDecorationTheme(
          filled: true,
          fillColor: Colors.white.withValues(alpha: 0.82),
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(27),
            borderSide: const BorderSide(color: AppColors.lightBorder),
          ),
          enabledBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(27),
            borderSide: const BorderSide(color: AppColors.lightBorder),
          ),
          focusedBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(27),
            borderSide: const BorderSide(color: AppColors.primary, width: 1.5),
          ),
          labelStyle: const TextStyle(color: AppColors.lightTextSecondary),
          hintStyle: const TextStyle(color: AppColors.lightTextSecondary),
          prefixIconColor: AppColors.primary,
        ),
        textButtonTheme: TextButtonThemeData(
          style: TextButton.styleFrom(
            foregroundColor: AppColors.primaryDark,
          ),
        ),
        elevatedButtonTheme: ElevatedButtonThemeData(
          style: ElevatedButton.styleFrom(
            backgroundColor: AppColors.primary,
            foregroundColor: Colors.white,
            padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(32),
            ),
            elevation: 0,
          ),
        ),
      ),
      darkTheme: ThemeData(
        useMaterial3: true,
        brightness: Brightness.dark,
        fontFamily: 'Georgia',
        scaffoldBackgroundColor: AppColors.darkBackgroundTop,
        primaryColor: AppColors.primary,
        colorScheme: const ColorScheme.dark(
          primary: AppColors.primary,
          secondary: AppColors.secondary,
          surface: AppColors.darkSurface,
          error: AppColors.danger,
          onPrimary: Colors.white,
          onSecondary: Colors.white,
          onSurface: AppColors.darkTextPrimary,
          onError: Colors.white,
        ),
        appBarTheme: const AppBarTheme(
          backgroundColor: Colors.transparent,
          foregroundColor: AppColors.darkTextPrimary,
          elevation: 0,
          centerTitle: false,
        ),
        cardColor: AppColors.darkSurface,
        textTheme: const TextTheme(
          headlineMedium: TextStyle(
            color: AppColors.darkTextPrimary,
            fontWeight: FontWeight.w700,
          ),
          bodyLarge: TextStyle(
            color: AppColors.darkTextPrimary,
          ),
          bodyMedium: TextStyle(
            color: AppColors.darkTextSecondary,
          ),
        ),
        inputDecorationTheme: InputDecorationTheme(
          filled: true,
          fillColor: AppColors.darkSurfaceSoft.withValues(alpha: 0.92),
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(27),
            borderSide: const BorderSide(color: AppColors.darkBorder),
          ),
          enabledBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(27),
            borderSide: const BorderSide(color: AppColors.darkBorder),
          ),
          focusedBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(27),
            borderSide: const BorderSide(color: AppColors.primary, width: 1.5),
          ),
          labelStyle: const TextStyle(color: AppColors.darkTextSecondary),
          hintStyle: const TextStyle(color: AppColors.darkTextSecondary),
          prefixIconColor: AppColors.accent,
        ),
        textButtonTheme: TextButtonThemeData(
          style: TextButton.styleFrom(
            foregroundColor: AppColors.accent,
          ),
        ),
        elevatedButtonTheme: ElevatedButtonThemeData(
          style: ElevatedButton.styleFrom(
            backgroundColor: AppColors.primary,
            foregroundColor: Colors.white,
            padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(32),
            ),
            elevation: 0,
          ),
        ),
      ),
      initialRoute: '/',
      routes: {
        '/': (context) => const SplashScreen(),
        '/login': (context) => const LoginScreen(),
        '/register': (context) => const RegisterScreen(),
        '/chat': (context) => const ChatScreen(),
        '/mood': (context) => const MoodDashboard(),
      },
    );
  }
}

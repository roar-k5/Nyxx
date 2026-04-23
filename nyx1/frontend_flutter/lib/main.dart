import 'package:flutter/material.dart';
import 'screens/splash_screen.dart';
import 'screens/login_screen.dart';
import 'screens/register_screen.dart';
import 'screens/chat_screen.dart';
import 'screens/mood_dashboard.dart';

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
      theme: ThemeData.dark().copyWith(
        scaffoldBackgroundColor: const Color(0xFF090225),
        primaryColor: const Color(0xFF9A69FF),
        colorScheme: const ColorScheme.dark(
          primary: Color(0xFF9A69FF),
          secondary: Color(0xFF69F1FF),
          surface: Color(0xFF18083B),
        ),
        inputDecorationTheme: InputDecorationTheme(
          filled: true,
          fillColor: const Color(0xFF0D0522).withValues(alpha: 0.66),
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(27),
            borderSide: BorderSide(color: Colors.white.withValues(alpha: 0.18)),
          ),
          enabledBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(27),
            borderSide: BorderSide(color: Colors.white.withValues(alpha: 0.18)),
          ),
          focusedBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(27),
            borderSide: const BorderSide(color: Color(0xFF9A69FF)),
          ),
        ),
        elevatedButtonTheme: ElevatedButtonThemeData(
          style: ElevatedButton.styleFrom(
            backgroundColor: const Color(0xFF9A69FF),
            foregroundColor: Colors.white,
            padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(32),
            ),
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

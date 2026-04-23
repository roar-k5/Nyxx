import 'dart:convert';
import 'dart:io' show Platform;

import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;

class CrisisHelpline {
  final String name;
  final String number;
  final String available;
  final String? languages;
  final bool whatsapp;

  CrisisHelpline({
    required this.name,
    required this.number,
    required this.available,
    this.languages,
    this.whatsapp = false,
  });

  factory CrisisHelpline.fromJson(Map<String, dynamic> json) {
    return CrisisHelpline(
      name: json['name']?.toString() ?? '',
      number: json['number']?.toString() ?? '',
      available: json['available']?.toString() ?? '',
      languages: json['languages']?.toString(),
      whatsapp: json['whatsapp'] == true,
    );
  }
}

class ApiResponse {
  final String response;
  final bool crisis;
  final String? crisisMessage;
  final List<CrisisHelpline>? helplines;
  final String? crisisLevel;
  final int? riskScore;
  final String? primaryEmotion;
  final String disclaimer;

  ApiResponse({
    required this.response,
    required this.crisis,
    this.crisisMessage,
    this.helplines,
    this.crisisLevel,
    this.riskScore,
    this.primaryEmotion,
    this.disclaimer = "I'm an AI companion, not a therapist.",
  });

  factory ApiResponse.fromJson(Map<String, dynamic> json) {
    List<CrisisHelpline>? helplines;
    if (json['helplines'] is List) {
      helplines = (json['helplines'] as List)
          .whereType<Map>()
          .map((item) =>
              CrisisHelpline.fromJson(Map<String, dynamic>.from(item)))
          .toList();
    }

    String? crisisLevel;
    int? riskScore;
    String? primaryEmotion;
    final analysis = json['analysis'];
    if (analysis is Map<String, dynamic>) {
      crisisLevel = analysis['crisis_level']?.toString();
      riskScore = (analysis['risk_score'] as num?)?.toInt();
      primaryEmotion = analysis['primary_emotion']?.toString();
    }

    return ApiResponse(
      response: json['response']?.toString() ?? '',
      crisis: json['crisis'] == true,
      crisisMessage: json['message']?.toString(),
      helplines: helplines,
      crisisLevel: crisisLevel,
      riskScore: riskScore,
      primaryEmotion: primaryEmotion ?? json['emotion']?.toString(),
      disclaimer: json['disclaimer']?.toString() ??
          "I'm an AI companion, not a therapist.",
    );
  }

  bool get isHighRisk =>
      crisisLevel == 'high' || crisisLevel == 'crisis' || (riskScore ?? 0) >= 7;

  bool get isCrisis =>
      crisis || crisisLevel == 'crisis' || (riskScore ?? 0) >= 9;
}

class AnalysisResponse {
  final String primaryEmotion;
  final double sentimentScore;
  final String intent;
  final String crisisLevel;
  final int riskScore;
  final List<String> keyConcerns;
  final String suggestedStrategy;

  const AnalysisResponse({
    required this.primaryEmotion,
    required this.sentimentScore,
    required this.intent,
    required this.crisisLevel,
    required this.riskScore,
    required this.keyConcerns,
    required this.suggestedStrategy,
  });

  factory AnalysisResponse.fromJson(Map<String, dynamic> json) {
    final rawConcerns = json['key_concerns'];
    return AnalysisResponse(
      primaryEmotion: json['primary_emotion']?.toString() ?? 'neutral',
      sentimentScore: (json['sentiment_score'] as num?)?.toDouble() ?? 0,
      intent: json['intent']?.toString() ?? 'general_chat',
      crisisLevel: json['crisis_level']?.toString() ?? 'none',
      riskScore: (json['risk_score'] as num?)?.toInt() ?? 0,
      keyConcerns: rawConcerns is List
          ? rawConcerns.map((item) => item.toString()).toList()
          : const [],
      suggestedStrategy: json['suggested_strategy']?.toString() ??
          'Respond with gentle empathy',
    );
  }
}

class ApiService {
  static const String _configuredBaseUrl =
      String.fromEnvironment('NYX_API_BASE_URL');

  static String get baseUrl {
    if (_configuredBaseUrl.isNotEmpty) return _configuredBaseUrl;
    if (kIsWeb) return 'http://localhost:5000';
    if (Platform.isAndroid) return 'http://10.0.2.2:5000';
    return 'http://localhost:5000';
  }

  static Future<ApiResponse> sendMessage(
    String message, {
    List<Map<String, dynamic>>? history,
    String userId = 'anonymous',
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/api/chat/send'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'message': message,
          'user_id': userId,
          'history': history ?? [],
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body) as Map<String, dynamic>;
        return ApiResponse.fromJson(data);
      }
      throw Exception('Failed: ${response.statusCode}');
    } catch (_) {
      return ApiResponse(
        response: "I'm having trouble connecting. Please try again.",
        crisis: false,
      );
    }
  }

  static Future<bool> checkHealth() async {
    try {
      final response = await http.get(Uri.parse('$baseUrl/health'));
      return response.statusCode == 200;
    } catch (_) {
      return false;
    }
  }

  static Future<AnalysisResponse> analyzeMessage(
    String message, {
    List<Map<String, dynamic>>? history,
    String userId = 'anonymous',
  }) async {
    final response = await http.post(
      Uri.parse('$baseUrl/api/analyze'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'message': message,
        'user_id': userId,
        'history': history ?? [],
      }),
    );

    if (response.statusCode != 200) {
      throw Exception('Analyze failed: ${response.statusCode}');
    }

    final data = jsonDecode(response.body) as Map<String, dynamic>;
    return AnalysisResponse.fromJson(data);
  }

  static Future<Map<String, dynamic>> getCrisisInfo() async {
    final response = await http.get(Uri.parse('$baseUrl/api/crisis-info'));
    if (response.statusCode == 200) {
      return jsonDecode(response.body) as Map<String, dynamic>;
    }
    throw Exception('Failed to get crisis info');
  }
}

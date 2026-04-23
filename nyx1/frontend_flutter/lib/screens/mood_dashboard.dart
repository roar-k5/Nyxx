import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import 'package:fl_chart/fl_chart.dart';

class MoodDashboard extends StatefulWidget {
  const MoodDashboard({super.key});

  @override
  State<MoodDashboard> createState() => _MoodDashboardState();
}

class _MoodDashboardState extends State<MoodDashboard> {
  Map<String, dynamic>? _moodData;
  bool _loading = true;
  String? _error;

  static const String baseUrl = 'http://localhost:5000';

  @override
  void initState() {
    super.initState();
    _fetchMood();
  }

  Future<void> _fetchMood() async {
    final prefs = await SharedPreferences.getInstance();
    final token = prefs.getString('token');

    try {
      final response = await http.get(
        Uri.parse('$baseUrl/api/mood/weekly'),
        headers: {
          if (token != null) 'Authorization': 'Bearer $token',
        },
      );

      final data = jsonDecode(response.body);

      if (response.statusCode == 200) {
        setState(() {
          _moodData = data;
          _loading = false;
        });
      } else {
        setState(() {
          _error = data['detail'] ?? 'Failed to load mood data';
          _loading = false;
        });
      }
    } catch (e) {
      setState(() {
        _error = 'Network error';
        _loading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: const Color(0xFF18083B),
        elevation: 0,
        title: const Text('Mood Dashboard'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: Colors.white),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [Color(0xFF090225), Color(0xFF18083B), Color(0xFF2D1150)],
          ),
        ),
        child: _loading
            ? const Center(
                child: CircularProgressIndicator(
                  valueColor: AlwaysStoppedAnimation<Color>(Color(0xFF9A69FF)),
                ),
              )
            : _error != null
                ? Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Text(
                          _error!,
                          style: const TextStyle(color: Colors.redAccent),
                        ),
                        const SizedBox(height: 16),
                        ElevatedButton(
                          onPressed: _fetchMood,
                          child: const Text('Retry'),
                        ),
                      ],
                    ),
                  )
                : _buildDashboard(),
      ),
    );
  }

  Widget _buildDashboard() {
    final emotion = _moodData?['emotion'] ?? 'neutral';
    final trend = _moodData?['trend'] ?? 'no_data';
    final stats = _moodData?['stats'] ?? {};
    final total = _moodData?['total_entries'] ?? 0;

    final emotionColor = _emotionColor(emotion);
    final trendIcon = _trendIcon(trend);
    final trendColor = _trendColor(trend);

    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildCard(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Current Mood',
                  style: TextStyle(
                    fontSize: 14,
                    color: Color(0xFFBDB0D8),
                  ),
                ),
                const SizedBox(height: 8),
                Row(
                  children: [
                    Container(
                      width: 16,
                      height: 16,
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        color: emotionColor,
                      ),
                    ),
                    const SizedBox(width: 8),
                    Text(
                      emotion.toUpperCase(),
                      style: TextStyle(
                        fontSize: 24,
                        fontWeight: FontWeight.bold,
                        color: emotionColor,
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
          const SizedBox(height: 16),
          _buildCard(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  '7-Day Trend',
                  style: TextStyle(
                    fontSize: 14,
                    color: Color(0xFFBDB0D8),
                  ),
                ),
                const SizedBox(height: 12),
                Row(
                  children: [
                    Icon(trendIcon, color: trendColor, size: 32),
                    const SizedBox(width: 12),
                    Text(
                      trend.toUpperCase(),
                      style: TextStyle(
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                        color: trendColor,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 4),
                Text(
                  '$total entries tracked',
                  style: TextStyle(
                    fontSize: 12,
                    color: Colors.white.withValues(alpha: 0.5),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 16),
          if (stats.isNotEmpty) ...[
            _buildCard(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Emotion Breakdown',
                    style: TextStyle(
                      fontSize: 14,
                      color: Color(0xFFBDB0D8),
                    ),
                  ),
                  const SizedBox(height: 16),
                  SizedBox(
                    height: 200,
                    child: _buildPieChart(stats),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),
            _buildCard(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Details',
                    style: TextStyle(
                      fontSize: 14,
                      color: Color(0xFFBDB0D8),
                    ),
                  ),
                  const SizedBox(height: 12),
                  ...stats.entries.map((e) {
                    final pct = e.value['percentage'] ?? 0;
                    final count = e.value['count'] ?? 0;
                    return Padding(
                      padding: const EdgeInsets.only(bottom: 8),
                      child: Row(
                        children: [
                          Container(
                            width: 12,
                            height: 12,
                            decoration: BoxDecoration(
                              shape: BoxShape.circle,
                              color: _emotionColor(e.key),
                            ),
                          ),
                          const SizedBox(width: 8),
                          Expanded(
                            child: Text(
                              '${e.key}  $count entries',
                              style: const TextStyle(
                                fontSize: 13,
                                color: Colors.white,
                              ),
                            ),
                          ),
                          Text(
                            '${pct.toStringAsFixed(1)}%',
                            style: TextStyle(
                              fontSize: 13,
                              fontWeight: FontWeight.bold,
                              color: _emotionColor(e.key),
                            ),
                          ),
                        ],
                      ),
                    );
                  }).toList(),
                ],
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildCard({required Widget child}) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            Colors.white.withValues(alpha: 0.08),
            Colors.white.withValues(alpha: 0.02),
          ],
        ),
        borderRadius: BorderRadius.circular(24),
        border: Border.all(
          color: Colors.white.withValues(alpha: 0.1),
        ),
      ),
      child: child,
    );
  }

  Widget _buildPieChart(Map<String, dynamic> stats) {
    final entries = stats.entries.toList();
    final total = entries.fold<int>(
      0,
      (sum, e) => sum + ((e.value['count'] ?? 0) as int),
    );

    if (total == 0) {
      return const Center(
        child: Text(
          'No data yet',
          style: TextStyle(color: Color(0xFFBDB0D8)),
        ),
      );
    }

    return PieChart(
      PieChartData(
        sectionsSpace: 2,
        centerSpaceRadius: 30,
        sections: entries.map((e) {
          final count = e.value['count'] ?? 0;
          final pct = count / total;
          return PieChartSectionData(
            color: _emotionColor(e.key),
            value: pct * 100,
            title: '${(pct * 100).toStringAsFixed(0)}%',
            radius: 60,
            titleStyle: const TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.bold,
              color: Colors.white,
            ),
          );
        }).toList(),
      ),
    );
  }

  Color _emotionColor(String emotion) {
    switch (emotion.toLowerCase()) {
      case 'happy':
      case 'calm':
        return const Color(0xFF9CFF8F);
      case 'sad':
      case 'sadness':
        return const Color(0xFF69A8FF);
      case 'anxious':
      case 'anxiety':
        return const Color(0xFFFFA500);
      case 'angry':
      case 'anger':
        return const Color(0xFFFF5F5F);
      case 'lonely':
      case 'loneliness':
        return const Color(0xFFBDB0D8);
      case 'distressed':
        return const Color(0xFFFF68D7);
      default:
        return const Color(0xFF9A69FF);
    }
  }

  IconData _trendIcon(String trend) {
    switch (trend.toLowerCase()) {
      case 'improving':
        return Icons.trending_up;
      case 'declining':
        return Icons.trending_down;
      default:
        return Icons.trending_flat;
    }
  }

  Color _trendColor(String trend) {
    switch (trend.toLowerCase()) {
      case 'improving':
        return const Color(0xFF9CFF8F);
      case 'declining':
        return const Color(0xFFFF5F5F);
      default:
        return const Color(0xFF69F1FF);
    }
  }
}

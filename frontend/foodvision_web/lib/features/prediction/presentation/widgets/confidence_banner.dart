import 'package:flutter/material.dart';

class ConfidenceBanner extends StatelessWidget {
  final double confidence;

  const ConfidenceBanner({super.key, required this.confidence});

  @override
  Widget build(BuildContext context) {
    final percent = (confidence * 100).toStringAsFixed(1);
    final isLow = confidence < 0.40;

    if (!isLow) return const SizedBox.shrink();

    return Container(
      margin: const EdgeInsets.only(bottom: 24),
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: const Color(0xFF1F1206),
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: const Color(0xFFF59E0B), width: 1.5),
        boxShadow: [
          BoxShadow(
            color: const Color(0xFFF59E0B).withValues(alpha: 0.2),
            blurRadius: 16,
          ),
        ],
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: const Color(0xFFF59E0B).withValues(alpha: 0.2),
              shape: BoxShape.circle,
            ),
            child: const Icon(
              Icons.warning_amber_rounded,
              color: Color(0xFFFBBF24),
              size: 24,
            ),
          ),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    const Text(
                      'ANOMALY DETECTED // 低共鳴警告',
                      style: TextStyle(
                        fontWeight: FontWeight.w900,
                        color: Color(0xFFFDE68A),
                        fontSize: 12,
                        letterSpacing: 1.2,
                      ),
                    ),
                    const Spacer(),
                    Text(
                      '$percent% RESONANCE',
                      style: const TextStyle(
                        fontWeight: FontWeight.bold,
                        color: Color(0xFFF59E0B),
                        fontSize: 11,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 6),
                Text(
                  'The neural net is detecting low signature affinity. Subject may be an uncatalogued dish, obscured angle, or non-food entity. Estimated closest culinary matches displayed below.',
                  style: TextStyle(
                    color: Colors.amber.shade200.withValues(alpha: 0.8),
                    fontSize: 12,
                    height: 1.4,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
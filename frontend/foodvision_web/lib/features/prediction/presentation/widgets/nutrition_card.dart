import 'package:flutter/material.dart';
import '../../data/models/nutrition_info.dart';

class NutritionCard extends StatelessWidget {
  final String foodName;

  const NutritionCard({super.key, required this.foodName});

  @override
  Widget build(BuildContext context) {
    final nutrition = NutritionInfo.forFood(foodName);

    return Container(
      margin: const EdgeInsets.symmetric(vertical: 20),
      padding: const EdgeInsets.all(22),
      decoration: BoxDecoration(
        color: const Color(0xFF0F172A),
        borderRadius: BorderRadius.circular(18),
        border: Border.all(color: const Color(0xFF7C3AED).withValues(alpha: 0.3)),
        boxShadow: [
          BoxShadow(
            color: const Color(0xFF7C3AED).withValues(alpha: 0.1),
            blurRadius: 20,
            spreadRadius: 2,
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header with Anime HUD Label
          Row(
            children: [
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                decoration: BoxDecoration(
                  color: const Color(0xFF7C3AED).withValues(alpha: 0.2),
                  borderRadius: BorderRadius.circular(6),
                  border: Border.all(color: const Color(0xFF7C3AED)),
                ),
                child: const Text(
                  'ENERGY MATRIX // 属性分析',
                  style: TextStyle(
                    color: Color(0xFFC4B5FD),
                    fontSize: 10,
                    fontWeight: FontWeight.w900,
                    letterSpacing: 1.5,
                  ),
                ),
              ),
              const Spacer(),
              Text(
                'SERVE: 100G',
                style: TextStyle(
                  color: Colors.grey.shade500,
                  fontSize: 10,
                  fontWeight: FontWeight.bold,
                  letterSpacing: 1.0,
                ),
              ),
            ],
          ),
          const SizedBox(height: 18),

          // 4 Glowing Macro Power Gauges
          Row(
            children: [
              _AnimeMacroPill(
                label: 'CALORIES',
                value: '${nutrition.calories}',
                unit: 'KCAL',
                color: const Color(0xFFEF4444), // Crimson Haki
                icon: Icons.local_fire_department,
              ),
              const SizedBox(width: 8),
              _AnimeMacroPill(
                label: 'PROTEIN',
                value: '${nutrition.protein}g',
                unit: 'POWER',
                color: const Color(0xFF3B82F6), // Cursed Blue
                icon: Icons.bolt,
              ),
              const SizedBox(width: 8),
              _AnimeMacroPill(
                label: 'CARBS',
                value: '${nutrition.carbs}g',
                unit: 'ENERGY',
                color: const Color(0xFFF59E0B), // Solar Amber
                icon: Icons.flash_on,
              ),
              const SizedBox(width: 8),
              _AnimeMacroPill(
                label: 'FAT',
                value: '${nutrition.fat}g',
                unit: 'RESERVE',
                color: const Color(0xFF10B981), // Emerald Toxic
                icon: Icons.shield,
              ),
            ],
          ),
          const SizedBox(height: 18),

          // Anime Dietary Attribute Badges
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: nutrition.tags.map((tag) {
              return Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
                decoration: BoxDecoration(
                  color: const Color(0xFF06B6D4).withValues(alpha: 0.08),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: const Color(0xFF06B6D4).withValues(alpha: 0.4)),
                ),
                child: Text(
                  '# ${tag.toUpperCase()}',
                  style: const TextStyle(
                    color: Color(0xFF67E8F9),
                    fontSize: 10,
                    fontWeight: FontWeight.w800,
                    letterSpacing: 1.0,
                  ),
                ),
              );
            }).toList(),
          ),
        ],
      ),
    );
  }
}

class _AnimeMacroPill extends StatelessWidget {
  final String label;
  final String value;
  final String unit;
  final Color color;
  final IconData icon;

  const _AnimeMacroPill({
    required this.label,
    required this.value,
    required this.unit,
    required this.color,
    required this.icon,
  });

  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 8),
        decoration: BoxDecoration(
          color: const Color(0xFF090E1A),
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: color.withValues(alpha: 0.4)),
          boxShadow: [
            BoxShadow(
              color: color.withValues(alpha: 0.15),
              blurRadius: 10,
            ),
          ],
        ),
        child: Column(
          children: [
            Icon(icon, color: color, size: 20),
            const SizedBox(height: 6),
            Text(
              value,
              style: TextStyle(
                fontWeight: FontWeight.w900,
                fontSize: 14,
                color: color,
                letterSpacing: 0.5,
              ),
            ),
            const SizedBox(height: 2),
            Text(
              label,
              style: TextStyle(
                color: Colors.grey.shade400,
                fontSize: 9,
                fontWeight: FontWeight.bold,
                letterSpacing: 1.0,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
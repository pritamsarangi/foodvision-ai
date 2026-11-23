import 'package:flutter/material.dart';

class AppTheme {
  // Shonen Anime Dark Palette
  static const Color voidBlack = Color(0xFF070A12);
  static const Color surfaceDark = Color(0xFF0F172A);
  static const Color surfaceCard = Color(0xFF131D31);
  static const Color borderGlow = Color(0xFF1E293B);

  // Auras & Energy
  static const Color cursedViolet = Color(0xFF7C3AED);
  static const Color neonCyan = Color(0xFF06B6D4);
  static const Color hakiCrimson = Color(0xFFEF4444);
  static const Color nenAmber = Color(0xFFF59E0B);
  static const Color auraGreen = Color(0xFF10B981);

  static ThemeData get darkAnimeTheme {
    return ThemeData(
      brightness: Brightness.dark,
      scaffoldBackgroundColor: voidBlack,
      fontFamily: 'Roboto', // Modern, clean
      colorScheme: const ColorScheme.dark(
        primary: cursedViolet,
        secondary: neonCyan,
        surface: surfaceDark,
        error: hakiCrimson,
      ),
      appBarTheme: const AppBarTheme(
        backgroundColor: Color(0xFF090E1A),
        elevation: 0,
        centerTitle: false,
        iconTheme: IconThemeData(color: neonCyan),
        titleTextStyle: TextStyle(
          color: Colors.white,
          fontSize: 20,
          fontWeight: FontWeight.w900,
          letterSpacing: 2.0,
        ),
      ),
      cardTheme: CardThemeData(
        color: surfaceDark,
        elevation: 8,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
          side: const BorderSide(color: Color(0xFF1E293B), width: 1),
        ),
      ),
    );
  }

  // Keep backward compatibility reference
  static ThemeData get lightTheme => darkAnimeTheme;
}

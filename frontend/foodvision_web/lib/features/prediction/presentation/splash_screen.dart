import 'dart:async';
import 'package:flutter/material.dart';
import 'prediction_screen.dart';

class SplashScreen extends StatefulWidget {
  const SplashScreen({super.key});

  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen>
    with SingleTickerProviderStateMixin {
  Timer? _timer;
  late AnimationController _pulseController;
  late Animation<double> _pulseAnimation;

  @override
  void initState() {
    super.initState();

    _pulseController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1400),
    )..repeat(reverse: true);

    _pulseAnimation = Tween<double>(begin: 0.4, end: 1.0).animate(
      CurvedAnimation(parent: _pulseController, curve: Curves.easeInOut),
    );

    // Auto-enter scanner after 3.5 seconds
    _timer = Timer(const Duration(milliseconds: 9500), _enterDomain);
  }

  void _enterDomain() {
    if (!mounted) return;
    _timer?.cancel();
    Navigator.of(context).pushReplacement(
      PageRouteBuilder(
        transitionDuration: const Duration(milliseconds: 700),
        pageBuilder: (context, animation, secondaryAnimation) =>
            const PredictionScreen(),
        transitionsBuilder: (context, animation, secondaryAnimation, child) {
          return FadeTransition(opacity: animation, child: child);
        },
      ),
    );
  }

  @override
  void dispose() {
    _timer?.cancel();
    _pulseController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final screenSize = MediaQuery.of(context).size;

    return Scaffold(
      backgroundColor: const Color(0xFF070A12),
      body: InkWell(
        onTap: _enterDomain, // Tap anywhere to skip directly
        splashColor: Colors.transparent,
        highlightColor: Colors.transparent,
        child: Stack(
          fit: StackFit.expand,
          children: [
            // 1. FULL-SCREEN HD ANIMATED COSMIC ENERGY (Native WebP)
            Image.asset(
              'assets/images/cosmic_energy.webp',
              fit: BoxFit.cover,
              width: double.infinity,
              height: double.infinity,
              errorBuilder: (context, error, stackTrace) {
                return const ColoredBox(color: Color(0xFF070A12));
              },
            ),

            // 2. CINEMATIC DARK RADIAL VIGNETTE
            Container(
              decoration: BoxDecoration(
                gradient: RadialGradient(
                  center: Alignment.center,
                  radius: 1.15,
                  colors: [
                    const Color(0xFF070A12).withValues(alpha: 0.25),
                    const Color(0xFF070A12).withValues(alpha: 0.65),
                    const Color(0xFF070A12).withValues(alpha: 0.95),
                  ],
                  stops: const [0.0, 0.65, 1.0],
                ),
              ),
            ),

            // 3. JAPANESE KANJI WATERMARK: 領域展開 (Domain Expansion)
            Center(
              child: Opacity(
                opacity: 0.08,
                child: Text(
                  '領域展開',
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    fontSize: screenSize.width > 600 ? 160 : 90,
                    fontWeight: FontWeight.w900,
                    color: const Color(0xFF7C3AED),
                    letterSpacing: 22,
                  ),
                ),
              ),
            ),

            // 4. FLOATING TACTICAL HUD
            Center(
              child: ConstrainedBox(
                constraints: const BoxConstraints(maxWidth: 580),
                child: Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 24),
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      // Special Grade Badge
                      AnimatedBuilder(
                        animation: _pulseAnimation,
                        builder: (context, child) {
                          return Container(
                            padding: const EdgeInsets.symmetric(
                              horizontal: 16,
                              vertical: 7,
                            ),
                            decoration: BoxDecoration(
                              color: const Color(0xFF7C3AED).withValues(
                                alpha: 0.20 * _pulseAnimation.value,
                              ),
                              borderRadius: BorderRadius.circular(20),
                              border: Border.all(
                                color: const Color(0xFF7C3AED).withValues(
                                  alpha: 0.8 * _pulseAnimation.value,
                                ),
                                width: 1.5,
                              ),
                              boxShadow: [
                                BoxShadow(
                                  color: const Color(0xFF7C3AED).withValues(
                                    alpha: 0.35 * _pulseAnimation.value,
                                  ),
                                  blurRadius: 18,
                                ),
                              ],
                            ),
                            child: const Row(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                Icon(
                                  Icons.bolt,
                                  size: 15,
                                  color: Color(0xFF06B6D4),
                                ),
                                SizedBox(width: 8),
                                Text(
                                  'SPECIAL GRADE // NEURAL VISION DOMAIN',
                                  style: TextStyle(
                                    color: Color(0xFFC4B5FD),
                                    fontWeight: FontWeight.w900,
                                    letterSpacing: 2.0,
                                    fontSize: 10,
                                  ),
                                ),
                              ],
                            ),
                          );
                        },
                      ),
                      const SizedBox(height: 28),

                      // App Title with Dual Glow
                      Text(
                        'FOODVISION AI',
                        textAlign: TextAlign.center,
                        style: TextStyle(
                          color: Colors.white,
                          fontSize: screenSize.width > 600 ? 44 : 32,
                          fontWeight: FontWeight.w900,
                          letterSpacing: 5.0,
                          shadows: const [
                            Shadow(
                              color: Color(0xFF7C3AED),
                              blurRadius: 32,
                            ),
                            Shadow(
                              color: Color(0xFF06B6D4),
                              blurRadius: 16,
                            ),
                          ],
                        ),
                      ),
                      const SizedBox(height: 32),

                      // Neon Progress Bar
                      ClipRRect(
                        borderRadius: BorderRadius.circular(4),
                        child: const LinearProgressIndicator(
                          backgroundColor: Color(0xFF1E293B),
                          valueColor: AlwaysStoppedAnimation<Color>(
                            Color(0xFF7C3AED),
                          ),
                          minHeight: 3,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),

            // 5. BOTTOM SKIP PROMPT
            Positioned(
              bottom: 24,
              left: 0,
              right: 0,
              child: Center(
                child: Text(
                  'TAP ANYWHERE TO ENTER DOMAIN ➔',
                  style: TextStyle(
                    color: Colors.grey.shade500,
                    fontSize: 10,
                    letterSpacing: 2.0,
                    fontWeight: FontWeight.w700,
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
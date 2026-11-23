import 'dart:async';
import 'package:flutter/material.dart';
import 'package:video_player/video_player.dart';
import 'prediction_screen.dart';

class SplashScreen extends StatefulWidget {
  const SplashScreen({super.key});

  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen>
    with SingleTickerProviderStateMixin {
  late VideoPlayerController _videoController;
  Timer? _timer;
  bool _isVideoInitialized = false;

  late AnimationController _pulseController;
  late Animation<double> _pulseAnimation;

  @override
  void initState() {
    super.initState();

    _pulseController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1200),
    )..repeat(reverse: true);

    _pulseAnimation = Tween<double>(begin: 0.5, end: 1.0).animate(
      CurvedAnimation(parent: _pulseController, curve: Curves.easeInOut),
    );

    // Load the local 2K/4K video from assets
        // Load your exact downloaded video file
    _videoController = VideoPlayerController.asset(
      'assets/videos/cosmic-fragments-moewalls-com.mp4',
    )..initialize().then((_) {
        if (!mounted) return;
        setState(() {
          _isVideoInitialized = true;
        });
        // Required for browser autoplay policy
        _videoController.setVolume(0.0);
        _videoController.setLooping(true);
        _videoController.play();
      }).catchError((error) {
        debugPrint('Video error: $error');
      });

    // Auto-enter scanner after 4 seconds
    _timer = Timer(const Duration(milliseconds: 10000), _enterDomain);
  }

  void _enterDomain() {
    if (!mounted) return;
    _timer?.cancel();
    _videoController.pause();
    Navigator.of(context).pushReplacement(
      PageRouteBuilder(
        transitionDuration: const Duration(milliseconds: 800),
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
    _videoController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final screenSize = MediaQuery.of(context).size;

    return Scaffold(
      backgroundColor: const Color(0xFF070A12),
      body: InkWell(
        onTap: _enterDomain, // Tap anywhere to skip instantly
        splashColor: Colors.transparent,
        highlightColor: Colors.transparent,
        child: Stack(
          fit: StackFit.expand,
          children: [
            // 1. FULL-SCREEN 2K/4K VIDEO LAYER
            if (_isVideoInitialized)
              SizedBox.expand(
                child: FittedBox(
                  fit: BoxFit.cover,
                  child: SizedBox(
                    width: _videoController.value.size.width > 0
                        ? _videoController.value.size.width
                        : screenSize.width,
                    height: _videoController.value.size.height > 0
                        ? _videoController.value.size.height
                        : screenSize.height,
                    child: VideoPlayer(_videoController),
                  ),
                ),
              )
            else
              const SizedBox.expand(
                child: ColoredBox(color: Color(0xFF070A12)),
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

            // 3. JAPANESE KANJI WATERMARK: 呪力解放 (Cursed Energy Unleashed)
            Center(
              child: Opacity(
                opacity: 0.08,
                child: Text(
                  '呪力解放',
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    fontSize: screenSize.width > 600 ? 150 : 80,
                    fontWeight: FontWeight.w900,
                    color: const Color(0xFF7C3AED),
                    letterSpacing: 20,
                  ),
                ),
              ),
            ),

            // 4. FLOATING HUD READOUT (CENTER)
            Center(
              child: ConstrainedBox(
                constraints: const BoxConstraints(maxWidth: 620),
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
                              vertical: 6,
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
                                    alpha: 0.4 * _pulseAnimation.value,
                                  ),
                                  blurRadius: 18,
                                ),
                              ],
                            ),
                            child: const Row(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                Icon(
                                  Icons.offline_bolt,
                                  size: 14,
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
                      const SizedBox(height: 24),

                      // High-Impact Glowing App Title
                      Text(
                        'FOODVISION AI',
                        textAlign: TextAlign.center,
                        style: TextStyle(
                          color: Colors.white,
                          fontSize: screenSize.width > 600 ? 46 : 32,
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
                      const SizedBox(height: 36),

                      // High-Tech Energy Charge Line
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

            // 5. BOTTOM BAR SKIP PROMPT
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
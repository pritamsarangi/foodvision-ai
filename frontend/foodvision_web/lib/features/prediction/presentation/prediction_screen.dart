import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import '../cubit/image_picker_cubit.dart';
import '../cubit/prediction_cubit.dart';
import '../../history/presentation/history_screen.dart';
import '../../history/cubit/history_cubit.dart';
import '../../history/data/repositories/history_repository.dart';
import '../../auth/cubit/auth_cubit.dart';
import '../../auth/cubit/auth_state.dart';
import '../../auth/presentation/auth_dialog.dart';
import 'widgets/confidence_banner.dart';
import 'widgets/nutrition_card.dart';

class PredictionScreen extends StatelessWidget {
  const PredictionScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF070A12),
      appBar: AppBar(
        title: Row(
          children: [
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
              decoration: BoxDecoration(
                gradient: const LinearGradient(
                  colors: [Color(0xFF7C3AED), Color(0xFF06B6D4)],
                ),
                borderRadius: BorderRadius.circular(6),
              ),
              child: const Text(
                'FV-270',
                style: TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.w900,
                  letterSpacing: 1.5,
                  color: Colors.white,
                ),
              ),
            ),
            const SizedBox(width: 12),
            const Text(
              'FOODVISION',
              style: TextStyle(
                fontWeight: FontWeight.w900,
                letterSpacing: 2.5,
                fontSize: 18,
              ),
            ),
          ],
        ),
        actions: [
          IconButton(
            tooltip: 'Archive History',
            icon: const Icon(Icons.history, color: Color(0xFF06B6D4)),
            onPressed: () {
              Navigator.of(context).push(
                MaterialPageRoute(
                  builder: (_) => BlocProvider(
                    create: (ctx) =>
                        HistoryCubit(ctx.read<HistoryRepository>())
                          ..loadHistory(),
                    child: const HistoryScreen(),
                  ),
                ),
              );
            },
          ),
          const SizedBox(width: 8),

          // User Profile / Sign In
          BlocBuilder<AuthCubit, AuthState>(
            builder: (context, state) {
              if (state is Authenticated) {
                return PopupMenuButton<String>(
                  tooltip: 'Hunter Account',
                  icon: Container(
                    padding: const EdgeInsets.all(2),
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      border: Border.all(
                        color: const Color(0xFF06B6D4),
                        width: 1.5,
                      ),
                    ),
                    child: CircleAvatar(
                      radius: 14,
                      backgroundColor: const Color(0xFF7C3AED),
                      child: Text(
                        state.user.email[0].toUpperCase(),
                        style: const TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.bold,
                          fontSize: 12,
                        ),
                      ),
                    ),
                  ),
                  onSelected: (value) {
                    if (value == 'logout') {
                      context.read<AuthCubit>().logout();
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(content: Text('Logged out of session')),
                      );
                    }
                  },
                  itemBuilder: (context) => [
                    PopupMenuItem(
                      enabled: false,
                      child: Text(
                        state.user.email,
                        style: const TextStyle(fontWeight: FontWeight.bold),
                      ),
                    ),
                    const PopupMenuDivider(),
                    const PopupMenuItem(
                      value: 'logout',
                      child: Row(
                        children: [
                          Icon(Icons.logout, size: 18, color: Colors.red),
                          SizedBox(width: 8),
                          Text('Sign Out', style: TextStyle(color: Colors.red)),
                        ],
                      ),
                    ),
                  ],
                );
              }

              // Guest Action
              return Padding(
                padding: const EdgeInsets.only(right: 12),
                child: TextButton.icon(
                  onPressed: () => AuthDialog.show(context),
                  icon: const Icon(
                    Icons.vpn_key_outlined,
                    size: 16,
                    color: Color(0xFF06B6D4),
                  ),
                  label: const Text(
                    'SIGN IN',
                    style: TextStyle(
                      color: Color(0xFF06B6D4),
                      fontWeight: FontWeight.w900,
                      letterSpacing: 1.2,
                      fontSize: 12,
                    ),
                  ),
                ),
              );
            },
          ),
        ],
      ),
      body: SingleChildScrollView(
        child: Center(
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 860),
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 32),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.center,
                children: [
                  // Title Header
                  Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 14,
                      vertical: 6,
                    ),
                    decoration: BoxDecoration(
                      color: const Color(0xFF7C3AED).withValues(alpha: 0.15),
                      borderRadius: BorderRadius.circular(20),
                      border: Border.all(
                        color: const Color(0xFF7C3AED).withValues(alpha: 0.4),
                      ),
                    ),
                    child: const Text(
                      'AI NEURAL RECOGNITION // 270 CLASSES',
                      style: TextStyle(
                        color: Color(0xFFC4B5FD),
                        fontWeight: FontWeight.w900,
                        letterSpacing: 1.5,
                        fontSize: 11,
                      ),
                    ),
                  ),
                  const SizedBox(height: 16),
                  Text(
                    'FOOD SCANNER & DOMAIN INTEL',
                    textAlign: TextAlign.center,
                    style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                      fontWeight: FontWeight.w900,
                      letterSpacing: 1.5,
                      color: Colors.white,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'Deploy EfficientNet-B0 vision neural net to decompose dishes, calculate nutritional energy, and identify recipes.',
                    textAlign: TextAlign.center,
                    style: TextStyle(
                      color: Colors.grey.shade400,
                      fontSize: 13,
                      height: 1.4,
                    ),
                  ),
                  const SizedBox(height: 32),

                  // ANIME SCANNER TARGET BOX
                  BlocBuilder<ImagePickerCubit, ImagePickerState>(
                    builder: (context, state) {
                      return Container(
                        width: double.infinity,
                        padding: const EdgeInsets.all(28),
                        decoration: BoxDecoration(
                          color: const Color(0xFF0B101E),
                          borderRadius: BorderRadius.circular(20),
                          border: Border.all(
                            color: state.imageBytes != null
                                ? const Color(0xFF06B6D4)
                                : const Color(0xFF1E293B),
                            width: 1.5,
                          ),
                          boxShadow: [
                            if (state.imageBytes != null)
                              BoxShadow(
                                color: const Color(
                                  0xFF06B6D4,
                                ).withValues(alpha: 0.15),
                                blurRadius: 24,
                              ),
                          ],
                        ),
                        child: Column(
                          children: [
                            if (state.imageBytes != null) ...[
                              ClipRRect(
                                borderRadius: BorderRadius.circular(14),
                                child: Image.memory(
                                  state.imageBytes!,
                                  height: 240,
                                  width: double.infinity,
                                  fit: BoxFit.contain,
                                ),
                              ),
                              const SizedBox(height: 16),
                              Container(
                                padding: const EdgeInsets.symmetric(
                                  horizontal: 12,
                                  vertical: 6,
                                ),
                                decoration: BoxDecoration(
                                  color: const Color(0xFF090E1A),
                                  borderRadius: BorderRadius.circular(8),
                                  border: Border.all(
                                    color: const Color(0xFF1E293B),
                                  ),
                                ),
                                child: Text(
                                  'TARGET: ${state.fileName?.toUpperCase() ?? "IMAGE"}',
                                  style: const TextStyle(
                                    color: Color(0xFF06B6D4),
                                    fontSize: 11,
                                    fontWeight: FontWeight.bold,
                                    letterSpacing: 1.2,
                                  ),
                                ),
                              ),
                            ] else ...[
                              Container(
                                padding: const EdgeInsets.all(22),
                                decoration: BoxDecoration(
                                  shape: BoxShape.circle,
                                  color: const Color(
                                    0xFF7C3AED,
                                  ).withValues(alpha: 0.12),
                                  border: Border.all(
                                    color: const Color(
                                      0xFF7C3AED,
                                    ).withValues(alpha: 0.4),
                                    width: 1.5,
                                  ),
                                  boxShadow: [
                                    BoxShadow(
                                      color: const Color(
                                        0xFF7C3AED,
                                      ).withValues(alpha: 0.25),
                                      blurRadius: 20,
                                    ),
                                  ],
                                ),
                                child: const Icon(
                                  Icons.radar_outlined,
                                  size: 46,
                                  color: Color(0xFF06B6D4),
                                ),
                              ),
                              const SizedBox(height: 18),
                              const Text(
                                'ENGAGE TARGET ACQUISITION',
                                style: TextStyle(
                                  fontSize: 16,
                                  fontWeight: FontWeight.w900,
                                  letterSpacing: 1.5,
                                  color: Colors.white,
                                ),
                              ),
                              const SizedBox(height: 6),
                              const Text(
                                'ACQUIRE TARGET DISH // DEPLOY 270-CLASS VISION DOMAIN',
                                style: TextStyle(
                                  color: Color(0xFF94A3B8),
                                  fontSize: 11,
                                  letterSpacing: 1.1,
                                  fontWeight: FontWeight.w600,
                                ),
                              ),
                            ],
                            const SizedBox(height: 24),

                            // Action buttons
                            Row(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                ElevatedButton.icon(
                                  onPressed: () async {
                                    final picker = context
                                        .read<ImagePickerCubit>();
                                    final prediction = context
                                        .read<PredictionCubit>();
                                    await picker.pickImage();
                                    if (context.mounted &&
                                        picker.state.imageBytes != null) {
                                      prediction.reset();
                                    }
                                  },
                                  style: ElevatedButton.styleFrom(
                                    backgroundColor: const Color(0xFF1E293B),
                                    foregroundColor: Colors.white,
                                    padding: const EdgeInsets.symmetric(
                                      horizontal: 20,
                                      vertical: 14,
                                    ),
                                    shape: RoundedRectangleBorder(
                                      borderRadius: BorderRadius.circular(10),
                                      side: const BorderSide(
                                        color: Color(0xFF334155),
                                      ),
                                    ),
                                  ),
                                  icon: const Icon(
                                    Icons.file_upload_outlined,
                                    size: 18,
                                  ),
                                  label: Text(
                                    state.imageBytes == null
                                        ? 'LOAD IMAGE'
                                        : 'SWITCH TARGET',
                                    style: const TextStyle(
                                      fontWeight: FontWeight.bold,
                                      fontSize: 12,
                                    ),
                                  ),
                                ),
                                if (state.imageBytes != null) ...[
                                  const SizedBox(width: 12),
                                  OutlinedButton.icon(
                                    onPressed: () {
                                      context
                                          .read<ImagePickerCubit>()
                                          .clearImage();
                                      context.read<PredictionCubit>().reset();
                                    },
                                    style: OutlinedButton.styleFrom(
                                      foregroundColor: Colors.red.shade400,
                                      side: BorderSide(
                                        color: Colors.red.shade900,
                                      ),
                                      padding: const EdgeInsets.symmetric(
                                        horizontal: 16,
                                        vertical: 14,
                                      ),
                                      shape: RoundedRectangleBorder(
                                        borderRadius: BorderRadius.circular(10),
                                      ),
                                    ),
                                    icon: const Icon(Icons.close, size: 16),
                                    label: const Text(
                                      'DISMISS',
                                      style: TextStyle(
                                        fontWeight: FontWeight.bold,
                                        fontSize: 12,
                                      ),
                                    ),
                                  ),
                                ],
                              ],
                            ),
                          ],
                        ),
                      );
                    },
                  ),
                  const SizedBox(height: 24),

                  // HIGH-OCTANE ANALYZE BUTTON
                  BlocBuilder<PredictionCubit, PredictionState>(
                    builder: (context, predictionState) {
                      return BlocBuilder<ImagePickerCubit, ImagePickerState>(
                        builder: (context, imageState) {
                          final canAnalyze =
                              imageState.imageBytes != null &&
                              !predictionState.isLoading;

                          return Column(
                            children: [
                              Container(
                                width: double.infinity,
                                height: 54,
                                decoration: BoxDecoration(
                                  borderRadius: BorderRadius.circular(12),
                                  gradient: canAnalyze
                                      ? const LinearGradient(
                                          colors: [
                                            Color(0xFF7C3AED),
                                            Color(0xFF06B6D4),
                                          ],
                                        )
                                      : null,
                                  color: canAnalyze
                                      ? null
                                      : const Color(0xFF1E293B),
                                  boxShadow: canAnalyze
                                      ? [
                                          BoxShadow(
                                            color: const Color(
                                              0xFF7C3AED,
                                            ).withValues(alpha: 0.4),
                                            blurRadius: 18,
                                            offset: const Offset(0, 4),
                                          ),
                                        ]
                                      : null,
                                ),
                                child: ElevatedButton(
                                  onPressed: canAnalyze
                                      ? () {
                                          context
                                              .read<PredictionCubit>()
                                              .predictImage(
                                                imageBytes:
                                                    imageState.imageBytes!,
                                                fileName:
                                                    imageState.fileName ??
                                                    'food.jpg',
                                              );
                                        }
                                      : null,
                                  style: ElevatedButton.styleFrom(
                                    backgroundColor: Colors.transparent,
                                    shadowColor: Colors.transparent,
                                    shape: RoundedRectangleBorder(
                                      borderRadius: BorderRadius.circular(12),
                                    ),
                                  ),
                                  child: predictionState.isLoading
                                      ? const Row(
                                          mainAxisAlignment:
                                              MainAxisAlignment.center,
                                          children: [
                                            SizedBox(
                                              width: 18,
                                              height: 18,
                                              child: CircularProgressIndicator(
                                                strokeWidth: 2,
                                                color: Colors.white,
                                              ),
                                            ),
                                            SizedBox(width: 14),
                                            Text(
                                              'DECOMPOSING NEURAL TENSORS...',
                                              style: TextStyle(
                                                fontWeight: FontWeight.w900,
                                                letterSpacing: 1.5,
                                                color: Colors.white,
                                              ),
                                            ),
                                          ],
                                        )
                                      : const Row(
                                          mainAxisAlignment:
                                              MainAxisAlignment.center,
                                          children: [
                                            Icon(
                                              Icons.bolt,
                                              color: Colors.white,
                                            ),
                                            SizedBox(width: 8),
                                            Text(
                                              'EXECUTE CLASSIFICATION MATRIX',
                                              style: TextStyle(
                                                fontWeight: FontWeight.w900,
                                                letterSpacing: 1.5,
                                                fontSize: 14,
                                                color: Colors.white,
                                              ),
                                            ),
                                          ],
                                        ),
                                ),
                              ),

                              // ERROR DISPLAY
                              if (predictionState.error != null) ...[
                                const SizedBox(height: 16),
                                Container(
                                  padding: const EdgeInsets.all(14),
                                  decoration: BoxDecoration(
                                    color: const Color(0xFF1E0B0B),
                                    borderRadius: BorderRadius.circular(10),
                                    border: Border.all(
                                      color: Colors.red.shade800,
                                    ),
                                  ),
                                  child: Text(
                                    predictionState.error!,
                                    style: TextStyle(
                                      color: Colors.red.shade200,
                                      fontSize: 13,
                                    ),
                                  ),
                                ),
                              ],

                              // CLASSIFIED TARGET RESULTS
                              if (predictionState.result != null) ...[
                                const SizedBox(height: 32),
                                Container(
                                  width: double.infinity,
                                  padding: const EdgeInsets.all(28),
                                  decoration: BoxDecoration(
                                    color: const Color(0xFF0F172A),
                                    borderRadius: BorderRadius.circular(20),
                                    border: Border.all(
                                      color: const Color(0xFF334155),
                                    ),
                                    boxShadow: [
                                      BoxShadow(
                                        color: Colors.black.withValues(
                                          alpha: 0.5,
                                        ),
                                        blurRadius: 30,
                                      ),
                                    ],
                                  ),
                                  child: Column(
                                    crossAxisAlignment:
                                        CrossAxisAlignment.start,
                                    children: [
                                      // 1. OOD Guardrail Warning
                                      ConfidenceBanner(
                                        confidence:
                                            predictionState.result!.confidence,
                                      ),

                                      // Header Tag
                                      Row(
                                        children: [
                                          Container(
                                            padding: const EdgeInsets.symmetric(
                                              horizontal: 10,
                                              vertical: 4,
                                            ),
                                            decoration: BoxDecoration(
                                              color: const Color(
                                                0xFF06B6D4,
                                              ).withValues(alpha: 0.15),
                                              borderRadius:
                                                  BorderRadius.circular(6),
                                              border: Border.all(
                                                color: const Color(0xFF06B6D4),
                                              ),
                                            ),
                                            child: const Text(
                                              'CLASSIFICATION RESULT',
                                              style: TextStyle(
                                                color: Color(0xFF67E8F9),
                                                fontWeight: FontWeight.w900,
                                                fontSize: 10,
                                                letterSpacing: 1.5,
                                              ),
                                            ),
                                          ),
                                          const Spacer(),
                                          Text(
                                            'MODEL: ${predictionState.result!.modelVersion.toUpperCase()}',
                                            style: TextStyle(
                                              color: Colors.grey.shade500,
                                              fontSize: 10,
                                              fontWeight: FontWeight.bold,
                                            ),
                                          ),
                                        ],
                                      ),
                                      const SizedBox(height: 16),

                                      // Dish Name
                                      Text(
                                        predictionState.result!.foodName
                                            .replaceAll('_', ' ')
                                            .toUpperCase(),
                                        style: const TextStyle(
                                          color: Colors.white,
                                          fontSize: 28,
                                          fontWeight: FontWeight.w900,
                                          letterSpacing: 1.5,
                                        ),
                                      ),
                                      const SizedBox(height: 8),

                                      // Confidence Bar with Anime Glow
                                      Row(
                                        children: [
                                          Text(
                                            'RESONANCE: ${(predictionState.result!.confidence * 100).toStringAsFixed(2)}%',
                                            style: const TextStyle(
                                              color: Color(0xFF06B6D4),
                                              fontWeight: FontWeight.w900,
                                              fontSize: 13,
                                              letterSpacing: 1.0,
                                            ),
                                          ),
                                          const SizedBox(width: 14),
                                          Expanded(
                                            child: ClipRRect(
                                              borderRadius:
                                                  BorderRadius.circular(6),
                                              child: LinearProgressIndicator(
                                                value: predictionState
                                                    .result!
                                                    .confidence,
                                                minHeight: 8,
                                                backgroundColor: const Color(
                                                  0xFF1E293B,
                                                ),
                                                valueColor:
                                                    const AlwaysStoppedAnimation(
                                                      Color(0xFF06B6D4),
                                                    ),
                                              ),
                                            ),
                                          ),
                                        ],
                                      ),

                                      // 2. Nutrition Energy Matrix
                                      NutritionCard(
                                        foodName:
                                            predictionState.result!.foodName,
                                      ),

                                      const SizedBox(height: 20),

                                      // Top 5 Alternate Resonance List
                                      const Text(
                                        'TOP 5 RESONANCE SPECTRA',
                                        style: TextStyle(
                                          color: Colors.white,
                                          fontSize: 13,
                                          fontWeight: FontWeight.w900,
                                          letterSpacing: 1.2,
                                        ),
                                      ),
                                      const SizedBox(height: 16),

                                      ...predictionState.result!.top5
                                          .asMap()
                                          .entries
                                          .map((entry) {
                                            final index = entry.key + 1;
                                            final food = entry.value;

                                            return Padding(
                                              padding: const EdgeInsets.only(
                                                bottom: 12,
                                              ),
                                              child: Container(
                                                padding:
                                                    const EdgeInsets.symmetric(
                                                      horizontal: 14,
                                                      vertical: 10,
                                                    ),
                                                decoration: BoxDecoration(
                                                  color: const Color(
                                                    0xFF090E1A,
                                                  ),
                                                  borderRadius:
                                                      BorderRadius.circular(10),
                                                  border: Border.all(
                                                    color: const Color(
                                                      0xFF1E293B,
                                                    ),
                                                  ),
                                                ),
                                                child: Row(
                                                  children: [
                                                    Text(
                                                      '#0$index',
                                                      style: const TextStyle(
                                                        color: Color(
                                                          0xFF7C3AED,
                                                        ),
                                                        fontWeight:
                                                            FontWeight.w900,
                                                        fontSize: 12,
                                                      ),
                                                    ),
                                                    const SizedBox(width: 12),
                                                    Expanded(
                                                      child: Text(
                                                        food.foodName
                                                            .replaceAll(
                                                              '_',
                                                              ' ',
                                                            )
                                                            .toUpperCase(),
                                                        style: const TextStyle(
                                                          color: Colors.white,
                                                          fontWeight:
                                                              FontWeight.bold,
                                                          fontSize: 13,
                                                        ),
                                                      ),
                                                    ),
                                                    Text(
                                                      '${(food.confidence * 100).toStringAsFixed(1)}%',
                                                      style: TextStyle(
                                                        color: Colors
                                                            .grey
                                                            .shade400,
                                                        fontWeight:
                                                            FontWeight.bold,
                                                        fontSize: 12,
                                                      ),
                                                    ),
                                                  ],
                                                ),
                                              ),
                                            );
                                          }),
                                    ],
                                  ),
                                ),
                              ],
                            ],
                          );
                        },
                      );
                    },
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}

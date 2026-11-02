import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import '../cubit/image_picker_cubit.dart';
import '../cubit/prediction_cubit.dart';

import '../../history/presentation/history_screen.dart';
import '../../history/cubit/history_cubit.dart';
import '../../history/data/repositories/history_repository.dart';
import '../../../core/network/api_client.dart';

class PredictionScreen extends StatelessWidget {
  const PredictionScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text(
          'FoodVision AI',
          overflow: TextOverflow.ellipsis,
          maxLines: 1,
        ),
        actions: [
          IconButton(
            tooltip: 'Prediction History',
            icon: const Icon(Icons.history),
            onPressed: () {
              Navigator.of(context).push(
                MaterialPageRoute(
                  builder: (_) => BlocProvider(
                    create: (_) =>
                        HistoryCubit(HistoryRepository(ApiClient()))
                          ..loadHistory(),
                    child: const HistoryScreen(),
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
            constraints: const BoxConstraints(maxWidth: 900),
            child: Padding(
              padding: const EdgeInsets.all(24),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.center,
                children: [
                  const Icon(
                    Icons.restaurant_menu,
                    size: 72,
                    color: Color(0xFF16A34A),
                  ),

                  const SizedBox(height: 24),

                  Text(
                    'Discover Your Food with AI',
                    textAlign: TextAlign.center,
                    style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
                  ),

                  const SizedBox(height: 12),

                  const Text(
                    'Upload a food image and let our AI identify it '
                    'from 270 different food categories.',
                    textAlign: TextAlign.center,
                  ),

                  const SizedBox(height: 32),

                  // IMAGE UPLOAD / PREVIEW
                  BlocBuilder<ImagePickerCubit, ImagePickerState>(
                    builder: (context, state) {
                      return Container(
                        width: double.infinity,
                        padding: const EdgeInsets.all(24),
                        decoration: BoxDecoration(
                          color: Colors.white,
                          borderRadius: BorderRadius.circular(20),
                          border: Border.all(color: const Color(0xFFE2E8F0)),
                        ),
                        child: Column(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            if (state.imageBytes != null) ...[
                              ClipRRect(
                                borderRadius: BorderRadius.circular(12),
                                child: Image.memory(
                                  state.imageBytes!,
                                  height: 200,
                                  width: double.infinity,
                                  fit: BoxFit.contain,
                                ),
                              ),

                              const SizedBox(height: 16),

                              Text(
                                state.fileName ?? 'Selected image',
                                textAlign: TextAlign.center,
                              ),
                            ] else ...[
                              const Icon(
                                Icons.cloud_upload_outlined,
                                size: 64,
                                color: Color(0xFF16A34A),
                              ),

                              const SizedBox(height: 16),

                              const Text(
                                'Upload Your Food Image',
                                style: TextStyle(
                                  fontSize: 20,
                                  fontWeight: FontWeight.w600,
                                ),
                              ),

                              const SizedBox(height: 8),

                              const Text('Supports JPG, PNG, and WebP'),
                            ],

                            const SizedBox(height: 24),

                            FilledButton.icon(
                              onPressed: () async {
                                final picker = context.read<ImagePickerCubit>();
                                final prediction = context
                                    .read<PredictionCubit>();

                                await picker.pickImage();

                                // Only clear the previous prediction when
                                // the selected image actually changes.
                                if (context.mounted &&
                                    picker.state.imageBytes != null &&
                                    !identical(
                                      state.imageBytes,
                                      picker.state.imageBytes,
                                    )) {
                                  prediction.reset();
                                }
                              },
                              icon: const Icon(
                                Icons.add_photo_alternate_outlined,
                              ),
                              label: Text(
                                state.imageBytes == null
                                    ? 'Choose Image'
                                    : 'Change Image',
                              ),
                            ),

                            if (state.imageBytes != null) ...[
                              const SizedBox(height: 12),

                              TextButton.icon(
                                onPressed: () {
                                  context.read<ImagePickerCubit>().clearImage();

                                  context.read<PredictionCubit>().reset();
                                },
                                icon: const Icon(Icons.delete_outline),
                                label: const Text('Remove Image'),
                              ),
                            ],

                            if (state.error != null) ...[
                              const SizedBox(height: 12),

                              Text(
                                state.error!,
                                textAlign: TextAlign.center,
                                style: const TextStyle(color: Colors.red),
                              ),
                            ],
                          ],
                        ),
                      );
                    },
                  ),

                  const SizedBox(height: 24),

                  // ANALYZE BUTTON / PREDICTION RESULTS
                  BlocBuilder<PredictionCubit, PredictionState>(
                    builder: (context, predictionState) {
                      return BlocBuilder<ImagePickerCubit, ImagePickerState>(
                        builder: (context, imageState) {
                          return Column(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              SizedBox(
                                width: double.infinity,
                                child: FilledButton.icon(
                                  onPressed:
                                      imageState.imageBytes == null ||
                                          predictionState.isLoading
                                      ? null
                                      : () {
                                          context
                                              .read<PredictionCubit>()
                                              .predictImage(
                                                imageBytes:
                                                    imageState.imageBytes!,
                                                fileName:
                                                    imageState.fileName ??
                                                    'food.jpg',
                                              );
                                        },
                                  icon: predictionState.isLoading
                                      ? const SizedBox(
                                          width: 18,
                                          height: 18,
                                          child: CircularProgressIndicator(
                                            strokeWidth: 2,
                                            color: Colors.white,
                                          ),
                                        )
                                      : const Icon(Icons.auto_awesome),
                                  label: Padding(
                                    padding: const EdgeInsets.symmetric(
                                      vertical: 12,
                                    ),
                                    child: Text(
                                      predictionState.isLoading
                                          ? 'Analyzing...'
                                          : 'Analyze Food',
                                    ),
                                  ),
                                ),
                              ),

                              // ERROR MESSAGE
                              if (predictionState.error != null) ...[
                                const SizedBox(height: 16),

                                Text(
                                  predictionState.error!,
                                  textAlign: TextAlign.center,
                                  style: const TextStyle(color: Colors.red),
                                ),
                              ],

                              // PREDICTION RESULTS
                              if (predictionState.result != null) ...[
                                const SizedBox(height: 32),

                                Container(
                                  width: double.infinity,
                                  padding: const EdgeInsets.all(24),
                                  decoration: BoxDecoration(
                                    color: Colors.white,
                                    borderRadius: BorderRadius.circular(20),
                                    border: Border.all(
                                      color: const Color(0xFFE2E8F0),
                                    ),
                                  ),
                                  child: Column(
                                    crossAxisAlignment:
                                        CrossAxisAlignment.start,
                                    children: [
                                      Text(
                                        'Prediction Result',
                                        style: Theme.of(context)
                                            .textTheme
                                            .titleLarge
                                            ?.copyWith(
                                              fontWeight: FontWeight.bold,
                                            ),
                                      ),

                                      const SizedBox(height: 20),

                                      Text(
                                        predictionState.result!.foodName,
                                        style: Theme.of(context)
                                            .textTheme
                                            .headlineSmall
                                            ?.copyWith(
                                              color: const Color(0xFF16A34A),
                                              fontWeight: FontWeight.bold,
                                            ),
                                      ),

                                      const SizedBox(height: 8),

                                      Text(
                                        'Confidence: '
                                        '${(predictionState.result!.confidence * 100).toStringAsFixed(2)}%',
                                      ),

                                      const SizedBox(height: 24),

                                      Text(
                                        'Top 5 Predictions',
                                        style: Theme.of(context)
                                            .textTheme
                                            .titleMedium
                                            ?.copyWith(
                                              fontWeight: FontWeight.bold,
                                            ),
                                      ),

                                      const SizedBox(height: 16),

                                      ...predictionState.result!.top5.map(
                                        (food) => Padding(
                                          padding: const EdgeInsets.only(
                                            bottom: 16,
                                          ),
                                          child: Column(
                                            crossAxisAlignment:
                                                CrossAxisAlignment.start,
                                            children: [
                                              Row(
                                                children: [
                                                  Expanded(
                                                    child: Text(food.foodName),
                                                  ),

                                                  Text(
                                                    '${(food.confidence * 100).toStringAsFixed(2)}%',
                                                  ),
                                                ],
                                              ),

                                              const SizedBox(height: 8),

                                              LinearProgressIndicator(
                                                value: food.confidence
                                                    .clamp(0.0, 1.0)
                                                    .toDouble(),
                                                minHeight: 8,
                                                borderRadius:
                                                    BorderRadius.circular(8),
                                                backgroundColor: const Color(
                                                  0xFFE2E8F0,
                                                ),
                                              ),
                                            ],
                                          ),
                                        ),
                                      ),
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

                  const SizedBox(height: 32),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}

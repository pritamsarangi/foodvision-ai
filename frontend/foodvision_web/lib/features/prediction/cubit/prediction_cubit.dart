
import 'dart:typed_data';

import 'package:dio/dio.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:foodvision_web/features/prediction/data/models/prediction_results.dart';
import '../data/repositories/prediction_repository.dart';

class PredictionState {
  final bool isLoading;
  final PredictionResult? result;
  final String? error;

  const PredictionState({
    this.isLoading = false,
    this.result,
    this.error,
  });
}

class PredictionCubit extends Cubit<PredictionState> {
  final PredictionRepository repository;

  PredictionCubit(this.repository) : super(const PredictionState());

  Future<void> predictImage({
    required Uint8List imageBytes,
    required String fileName,
  }) async {
    emit(const PredictionState(isLoading: true));

    try {
      final result = await repository.predict(
        imageBytes: imageBytes,
        fileName: fileName,
      );

      emit(PredictionState(result: result));
    } on DioException catch (e) {
      final detail = e.response?.data is Map
          ? (e.response!.data as Map)['detail']?.toString()
          : null;

      emit(PredictionState(
        error: detail ?? 'Cannot connect to the prediction service.',
      ));
    } catch (_) {
      emit(const PredictionState(
        error: 'Unable to process this image.',
      ));
    }
  }

  void reset() {
    emit(const PredictionState());
  }
}


import 'dart:typed_data';

import 'package:bloc_test/bloc_test.dart';
import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:foodvision_web/features/prediction/data/models/prediction_results.dart';
import 'package:mocktail/mocktail.dart';

import 'package:foodvision_web/features/prediction/cubit/prediction_cubit.dart';
import 'package:foodvision_web/features/prediction/data/repositories/prediction_repository.dart';

class MockPredictionRepository extends Mock
    implements PredictionRepository {}

void main() {
  late MockPredictionRepository repository;

  setUpAll(() {
    registerFallbackValue(Uint8List(0));
  });

  setUp(() {
    repository = MockPredictionRepository();
  });

  final imageBytes = Uint8List.fromList([1, 2, 3]);

   const fakeResult = PredictionResult(
    predictionId: 'test-123',
    foodName: 'Pizza',
    confidence: 0.95,
    modelVersion: 'efficientnet-b0-finetuned-v1',
    top5: [
      FoodPrediction(foodName: 'Pizza', confidence: 0.95),
      FoodPrediction(foodName: 'Burger', confidence: 0.03),
    ],
  );

  blocTest<PredictionCubit, PredictionState>(
    'emits loading and prediction result on success',
    build: () {
      when(
        () => repository.predict(
          imageBytes: any(named: 'imageBytes'),
          fileName: any(named: 'fileName'),
        ),
      ).thenAnswer((_) async => fakeResult);

      return PredictionCubit(repository);
    },
    act: (cubit) => cubit.predictImage(
      imageBytes: imageBytes,
      fileName: 'pizza.jpg',
    ),
    expect: () => [
      isA<PredictionState>()
          .having((s) => s.isLoading, 'loading', true),
      isA<PredictionState>()
          .having((s) => s.isLoading, 'loading', false)
          .having((s) => s.result?.foodName, 'food name', 'Pizza')
          .having((s) => s.result?.confidence, 'confidence', 0.95),
    ],
  );

  blocTest<PredictionCubit, PredictionState>(
    'emits error when API request fails',
    build: () {
      when(
        () => repository.predict(
          imageBytes: any(named: 'imageBytes'),
          fileName: any(named: 'fileName'),
        ),
      ).thenThrow(
        DioException(
          requestOptions: RequestOptions(path: '/api/v1/predict'),
          type: DioExceptionType.connectionError,
          message: 'Connection refused',
        ),
      );

      return PredictionCubit(repository);
    },
    act: (cubit) => cubit.predictImage(
      imageBytes: imageBytes,
      fileName: 'pizza.jpg',
    ),
    expect: () => [
      isA<PredictionState>()
          .having((s) => s.isLoading, 'loading', true),
      isA<PredictionState>()
          .having(
            (s) => s.error,
            'error message',
            'Cannot connect to the prediction service.',
          ),
    ],
  );

  blocTest<PredictionCubit, PredictionState>(
    'clears prediction state on reset',
    build: () {
      when(
        () => repository.predict(
          imageBytes: any(named: 'imageBytes'),
          fileName: any(named: 'fileName'),
        ),
      ).thenAnswer((_) async => fakeResult);

      return PredictionCubit(repository);
    },
    act: (cubit) async {
      await cubit.predictImage(
        imageBytes: imageBytes,
        fileName: 'pizza.jpg',
      );

      cubit.reset();
    },
    expect: () => [
      isA<PredictionState>()
          .having((s) => s.isLoading, 'loading', true),
      isA<PredictionState>()
          .having((s) => s.result?.foodName, 'food name', 'Pizza'),
      isA<PredictionState>()
          .having((s) => s.result, 'result', null)
          .having((s) => s.error, 'error', null)
          .having((s) => s.isLoading, 'loading', false),
    ],
  );
}

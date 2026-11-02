
import 'package:bloc_test/bloc_test.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';

import 'package:foodvision_web/features/history/cubit/history_cubit.dart';
import 'package:foodvision_web/features/history/data/models/prediction_history.dart';
import 'package:foodvision_web/features/history/data/repositories/history_repository.dart';

class MockHistoryRepository extends Mock implements HistoryRepository {}

void main() {
  late MockHistoryRepository repository;

  setUp(() {
    repository = MockHistoryRepository();
  });

  final fakeHistory = [
    PredictionHistory(
      id: 'test-123',
      foodName: 'Pizza',
      confidence: 0.95,
      createdAt: DateTime(2026, 11, 2),
      top5: const [
        HistoryFoodPrediction(
          foodName: 'Pizza',
          confidence: 0.95,
        ),
      ],
    ),
  ];

  blocTest<HistoryCubit, HistoryState>(
    'emits loading and prediction history on success',
    build: () {
      when(() => repository.getHistory())
          .thenAnswer((_) async => fakeHistory);

      return HistoryCubit(repository);
    },
    act: (cubit) => cubit.loadHistory(),
    expect: () => [
      isA<HistoryState>()
          .having((state) => state.isLoading, 'loading', true),
      isA<HistoryState>()
          .having((state) => state.isLoading, 'loading', false)
          .having((state) => state.predictions.length, 'count', 1)
          .having(
            (state) => state.predictions.first.foodName,
            'food name',
            'Pizza',
          ),
    ],
  );

  blocTest<HistoryCubit, HistoryState>(
    'emits error when history API fails',
    build: () {
      when(() => repository.getHistory())
          .thenThrow(Exception('Server unavailable'));

      return HistoryCubit(repository);
    },
    act: (cubit) => cubit.loadHistory(),
    expect: () => [
      isA<HistoryState>()
          .having((state) => state.isLoading, 'loading', true),
      isA<HistoryState>()
          .having(
            (state) => state.error,
            'error',
            'Unable to load prediction history.',
          ),
    ],
  );
}

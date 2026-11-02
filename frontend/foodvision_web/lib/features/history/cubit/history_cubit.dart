
import 'package:flutter_bloc/flutter_bloc.dart';

import '../data/models/prediction_history.dart';
import '../data/repositories/history_repository.dart';

class HistoryState {
  final bool isLoading;
  final List<PredictionHistory> predictions;
  final String? error;

  const HistoryState({
    this.isLoading = false,
    this.predictions = const [],
    this.error,
  });
}

class HistoryCubit extends Cubit<HistoryState> {
  final HistoryRepository repository;

  HistoryCubit(this.repository) : super(const HistoryState());

  Future<void> loadHistory() async {
    emit(HistoryState(
      isLoading: true,
      predictions: state.predictions,
    ));

    try {
      final records = await repository.getHistory();

      emit(HistoryState(predictions: records));
    } catch (_) {
      emit(HistoryState(
        predictions: state.predictions,
        error: 'Unable to load prediction history.',
      ));
    }
  }
}


import 'package:dio/dio.dart';

import '../../../../core/network/api_client.dart';
import '../models/prediction_history.dart';

class HistoryRepository {
  final Dio _dio;

  HistoryRepository(ApiClient apiClient) : _dio = apiClient.dio;

  Future<List<PredictionHistory>> getHistory() async {
    final response = await _dio.get('/api/v1/predictions');

    final records = response.data as List;

    return records
        .map(
          (item) => PredictionHistory.fromJson(
            Map<String, dynamic>.from(item as Map),
          ),
        )
        .toList();
  }
}

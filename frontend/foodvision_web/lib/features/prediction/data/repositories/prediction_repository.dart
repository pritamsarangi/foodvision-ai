
import 'dart:typed_data';

import 'package:dio/dio.dart';
import 'package:foodvision_web/features/prediction/data/models/prediction_results.dart';

import '../../../../core/network/api_client.dart';

class PredictionRepository {
  final Dio _dio;

  PredictionRepository(ApiClient apiClient) : _dio = apiClient.dio;

  Future<PredictionResult> predict({
    required Uint8List imageBytes,
    required String fileName,
  }) async {
    final formData = FormData.fromMap({
      'file': MultipartFile.fromBytes(
        imageBytes,
        filename: fileName,
      ),
    });

    final response = await _dio.post(
      '/api/v1/predict',
      data: formData,
    );

    return PredictionResult.fromJson(
      Map<String, dynamic>.from(response.data as Map),
    );
  }
}

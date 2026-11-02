
class FoodPrediction {
  final String foodName;
  final double confidence;

  const FoodPrediction({
    required this.foodName,
    required this.confidence,
  });

  factory FoodPrediction.fromJson(Map<String, dynamic> json) {
    return FoodPrediction(
      foodName: json['food_name'] as String,
      confidence: (json['confidence'] as num).toDouble(),
    );
  }
}

class PredictionResult {
  final String? predictionId;
  final String foodName;
  final double confidence;
  final List<FoodPrediction> top5;
  final String modelVersion;

  const PredictionResult({
    required this.predictionId,
    required this.foodName,
    required this.confidence,
    required this.top5,
    required this.modelVersion,
  });

  factory PredictionResult.fromJson(Map<String, dynamic> json) {
    return PredictionResult(
      predictionId: json['prediction_id'] as String?,
      foodName: json['food_name'] as String,
      confidence: (json['confidence'] as num).toDouble(),
      top5: (json['top_5'] as List)
          .map((item) =>
              FoodPrediction.fromJson(item as Map<String, dynamic>))
          .toList(),
      modelVersion: json['model_version'] as String,
    );
  }
}


class PredictionHistory {
  final String id;
  final String foodName;
  final double confidence;
  final DateTime createdAt;
  final List<HistoryFoodPrediction> top5;

  const PredictionHistory({
    required this.id,
    required this.foodName,
    required this.confidence,
    required this.createdAt,
    required this.top5,
  });

  factory PredictionHistory.fromJson(Map<String, dynamic> json) {
    return PredictionHistory(
      id: json['id'].toString(),
      foodName: json['food_name'] as String,
      confidence: (json['confidence'] as num).toDouble(),
      createdAt: DateTime.parse(json['created_at'] as String),
      top5: (json['top_5'] as List? ?? [])
          .map((item) => HistoryFoodPrediction.fromJson(
                Map<String, dynamic>.from(item as Map),
              ))
          .toList(),
    );
  }
}

class HistoryFoodPrediction {
  final String foodName;
  final double confidence;

  const HistoryFoodPrediction({
    required this.foodName,
    required this.confidence,
  });

  factory HistoryFoodPrediction.fromJson(Map<String, dynamic> json) {
    return HistoryFoodPrediction(
      foodName: json['food_name'] as String,
      confidence: (json['confidence'] as num).toDouble(),
    );
  }
}

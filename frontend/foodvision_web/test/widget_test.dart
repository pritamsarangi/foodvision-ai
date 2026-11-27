import 'package:flutter_test/flutter_test.dart';
import 'package:foodvision_web/features/auth/data/repositories/auth_repository.dart';
import 'package:foodvision_web/features/history/data/repositories/history_repository.dart';
import 'package:foodvision_web/features/prediction/data/repositories/prediction_repository.dart';
import 'package:foodvision_web/main.dart';
import 'package:mocktail/mocktail.dart';

class MockAuthRepository extends Mock implements AuthRepository {}
class MockPredictionRepository extends Mock implements PredictionRepository {}
class MockHistoryRepository extends Mock implements HistoryRepository {}

void main() {
  testWidgets('FoodVision splash screen loads on startup', (tester) async {
    final authRepo = MockAuthRepository();
    final predRepo = MockPredictionRepository();
    final histRepo = MockHistoryRepository();

    when(() => authRepo.isAuthenticated).thenReturn(false);

    await tester.pumpWidget(FoodVisionApp(
      authRepository: authRepo,
      predictionRepository: predRepo,
      historyRepository: histRepo,
    ));

    expect(find.text('FOODVISION AI'), findsOneWidget);
    expect(find.text('TAP ANYWHERE TO ENTER DOMAIN ➔'), findsOneWidget);
  });
}
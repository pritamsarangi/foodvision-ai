import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:foodvision_web/features/prediction/presentation/splash_screen.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'core/network/api_client.dart';
import 'core/theme/app_theme.dart';
import 'features/auth/cubit/auth_cubit.dart';
import 'features/auth/data/repositories/auth_repository.dart';
import 'features/history/data/repositories/history_repository.dart';
import 'features/prediction/cubit/image_picker_cubit.dart';
import 'features/prediction/cubit/prediction_cubit.dart';
import 'features/prediction/data/repositories/prediction_repository.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  final prefs = await SharedPreferences.getInstance();

  // Create repository holder so ApiClient can access the latest token dynamically
  late final AuthRepository authRepository;
  final apiClient = ApiClient(tokenProvider: () => authRepository.accessToken);
  authRepository = AuthRepository(apiClient, prefs);

  final predictionRepository = PredictionRepository(apiClient);
  final historyRepository = HistoryRepository(apiClient);

  runApp(FoodVisionApp(
    authRepository: authRepository,
    predictionRepository: predictionRepository,
    historyRepository: historyRepository,
  ));
}

class FoodVisionApp extends StatelessWidget {
  final AuthRepository authRepository;
  final PredictionRepository predictionRepository;
  final HistoryRepository historyRepository;

  const FoodVisionApp({
    super.key,
    required this.authRepository,
    required this.predictionRepository,
    required this.historyRepository,
  });

  @override
  Widget build(BuildContext context) {
    return MultiRepositoryProvider(
      providers: [
        RepositoryProvider.value(value: authRepository),
        RepositoryProvider.value(value: predictionRepository),
        RepositoryProvider.value(value: historyRepository),
      ],
      child: MultiBlocProvider(
        providers: [
          BlocProvider(
            create: (_) => AuthCubit(authRepository)..checkAuthStatus(),
          ),
          BlocProvider(create: (_) => ImagePickerCubit()),
          BlocProvider(create: (_) => PredictionCubit(predictionRepository)),
        ],
        child: MaterialApp(
          title: 'FoodVision AI',
          debugShowCheckedModeBanner: false,
          theme: AppTheme.lightTheme,
          home: const SplashScreen(),
        ),
      ),
    );
  }
}
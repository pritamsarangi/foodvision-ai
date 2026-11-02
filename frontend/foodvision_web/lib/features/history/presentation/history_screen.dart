
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import '../cubit/history_cubit.dart';

class HistoryScreen extends StatelessWidget {
  const HistoryScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Prediction History'),
        actions: [
          IconButton(
            tooltip: 'Refresh',
            onPressed: () => context.read<HistoryCubit>().loadHistory(),
            icon: const Icon(Icons.refresh),
          ),
        ],
      ),
      body: BlocBuilder<HistoryCubit, HistoryState>(
        builder: (context, state) {
          if (state.isLoading && state.predictions.isEmpty) {
            return const Center(child: CircularProgressIndicator());
          }

          if (state.error != null && state.predictions.isEmpty) {
            return Center(
              child: Text(state.error!),
            );
          }

          if (state.predictions.isEmpty) {
            return const Center(
              child: Text('No predictions yet. Analyze your first food!'),
            );
          }

          return RefreshIndicator(
            onRefresh: () => context.read<HistoryCubit>().loadHistory(),
            child: ListView.builder(
              padding: const EdgeInsets.all(16),
              itemCount: state.predictions.length,
              itemBuilder: (context, index) {
                final prediction = state.predictions[index];

                return Card(
                  margin: const EdgeInsets.only(bottom: 12),
                  child: ExpansionTile(
                    title: Text(
                      prediction.foodName,
                      style: const TextStyle(fontWeight: FontWeight.bold),
                    ),
                    subtitle: Text(
                      'Confidence: ${(prediction.confidence * 100).toStringAsFixed(2)}%'
                      '\n${prediction.createdAt.toLocal()}',
                    ),
                    children: prediction.top5.map((food) {
                      return ListTile(
                        title: Text(food.foodName),
                        trailing: Text(
                          '${(food.confidence * 100).toStringAsFixed(2)}%',
                        ),
                      );
                    }).toList(),
                  ),
                );
              },
            ),
          );
        },
      ),
    );
  }
}

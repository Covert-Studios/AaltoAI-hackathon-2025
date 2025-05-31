from collections import Counter

# Use predicted_labels or true_labels
counts = Counter(predicted_labels)
sorted_counts = sorted(counts.items())

labels = [class_names[i] for i, _ in sorted_counts]
values = [count for _, count in sorted_counts]

plt.figure(figsize=(12, 6))
plt.bar(labels, values)
plt.xticks(rotation=90)
plt.ylabel("Count")
plt.title("Predicted Class Distribution")
plt.tight_layout()
plt.show()

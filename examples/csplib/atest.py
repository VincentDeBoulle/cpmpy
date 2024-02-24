import psutil

def main(n):
    # Function to determine whether the number is even or odd
    if n % 2 == 0:
        print("The number is even")
    else:
        print("The number is odd")

if __name__ == '__main__':
    initial_memory = psutil.Process().memory_info().rss
    main(4)
    final_memory = psutil.Process().memory_info().rss
    memory_usage = final_memory - initial_memory

    print(f"Overall Memory Usage: {memory_usage / (1024 ** 2):.2f} MB")

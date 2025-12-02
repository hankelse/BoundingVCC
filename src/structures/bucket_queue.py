from collections import deque

'''
A class used to efficently calculate degeneracy orderings based on Matula and Beck's 1983 paper.

The bucket queue is a list of "deque"s which are doubly linked lists

'''
class BucketQueue:
    def __init__(self, num_buckets): # Makes buckets labelled 0..num_buckets-1
        self.buckets = [deque() for _ in range(num_buckets + 1)]
        self.curr_min = 0
        self.size = 0

    def push(self, key, item):
        self.buckets[key].append(item)
        self.size += 1
        if key < self.curr_min: self.curr_min = key # Make sure that curr_min points to the first non-empty bucket

    def pop_min(self):
        while self.curr_min <= len(self.buckets) - 1 and not self.buckets[self.curr_min]:
            self.curr_min += 1
        if self.curr_min == len(self.buckets):
            return None
        self.size -= 1
        return self.buckets[self.curr_min].popleft()

    def is_empty(self):
        return self.size == 0
    


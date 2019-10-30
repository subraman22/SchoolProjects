/**
 * ParallelQuickSort.java
 * CS 5006 Homework 5
 * Summer 2 2019
 * Rohan Subramaniam
 * 8/6/19
 */
import java.util.concurrent.ForkJoinPool;
import java.util.concurrent.RecursiveAction;

/**
 * This class is an implementation of QuickSort using parallel threads.
 * Adapted from lecture material by Philip Gust
 *
 *
 */
@SuppressWarnings("serial")
public class ParallelQuickSort extends RecursiveAction {

    /** value array, and indexes to interval [lo, hi] in the array. */
    int[] values;
    int lo, hi;

    /**
     * Construct parallel sorter for values array from 
     * [lo, hi] using quicksort
     * @param values the array to sort
     * @param lo index of first element to sort
     * @param hi index of last value to sort
     */
    ParallelQuickSort(int[] values, int lo, int hi) {
        this.values = values;
        this.lo = lo;
        this.hi = hi;
    }

    /**
     * Swap array values in-place.
     *
     * @param vals the array
     * @param i the first index
     * @param j the second index
     */
    void swap(int[] vals, int i, int j) {
        int temp = vals[i];
        vals[i] = vals[j];
        vals[j] = temp;
    }

    /**
     * Partition to array and return the pivot point index.
     *
     * @param vals the array
     * @param lo the low index
     * @param hi the high index
     * @return the pivot point index
     */
    int partition (int vals[], int lo, int hi) {
        int pv = hi;    	// pivot about hi value
        int i = lo-1;       // index of smaller element
        for (int j = lo; j <= hi-1;  j++) {
            if (vals[j] <= vals[pv]) {
                i++; // increment index of smaller element
                swap(vals, i, j);
            }
        }
        i++; // increment index of smaller element
        swap(vals, i, pv); // pivot is put in the correct place
        return i;
    }

    /**
     * Arrays of one are by definition sorted. Otherwise invoke sub tasks on the left and right
     * portions of the array around the pivot until all sub arrays are sorted.
     *
     * @see java.util.concurrent.RecursiveTask#compute()
     */
    @Override
    protected void compute() {

        if (lo >= hi // array of size 1 is sorted
                ||  (ForkJoinPool.getCommonPoolParallelism() == 1)) {
            System.out.printf("%s: %d %d\n",Thread.currentThread().getName(), lo, hi);
        } else {
            int p = partition(values, lo, hi); // returns index where the pivot ends up, sort both sides after
            System.out.printf("%s: %d %d %d\n",Thread.currentThread().getName(), lo, p, hi);

            // run sub=tasks, automatically forking for one of the two,
            // and wait for completion of both sub-tasks
            invokeAll(new ParallelQuickSort(values, lo, p - 1),
                    new ParallelQuickSort(values, p + 1, hi));

        }
    }

    /**
     * Parallel sort an array
     * @param values
     */
    static public void sort(int[] values) {
        ForkJoinPool.commonPool().invoke(
                new ParallelQuickSort(values, 0, values.length - 1));
    }
    /**
     * Sort sample array using parallel sorter.
     * @param args
     */
    public static void main(String[] args) {
        int[] values = {0, 2, 10, 5, -6, 7, 20, 2};
        ParallelQuickSort.sort(values);
        for (int val : values) {
            System.out.printf("%d ", val);
        }
        System.out.println();
        int[] values2 = {33, 200, 10, -5, -6, 7, -20, 2};
        ParallelQuickSort.sort(values2);
        for (int val : values2) {
            System.out.printf("%d ", val);
        }
        System.out.println();
        int[] values3 = {100, 20, 10, 0, -2, -7, -20, -22};
        ParallelQuickSort.sort(values3);
        for (int val : values3) {
            System.out.printf("%d ", val);
        }
        System.out.println();
    }
}
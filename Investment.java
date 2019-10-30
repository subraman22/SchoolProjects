/**
 * Investment.java
 * 
 * This program selects an optimal investment portfolio
 * using a greedy algorithm that prioritizes the most
 * shares of the highest yielding bond first.
 * by Rohan Subramaniam, skeleton code from P. Gust
 * 
 */
import java.lang.reflect.Array;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collection;
import java.util.Comparator;
import java.util.PriorityQueue;

import org.junit.FixMethodOrder;
import org.junit.Test;
import org.junit.runner.JUnitCore;
import org.junit.runner.Result;
import org.junit.runner.notification.Failure;
import org.junit.runners.MethodSorters;

import static org.junit.Assert.assertEquals;

/**
 * This is a wrapper class for the Bond and 
 * HighestBondYieldComparator, and the unit
 * test class TestInvestment.
 */
public class Investment {	
	/**
	 * This class represents a Bond.	 *
	 */
	static public final class Bond {
		// your code here

		// Fields for the details of each individual bond.
		public String name;
		public float shares, cost, yield;
		/**
		 * Full constructor for Bond with all fields
		 * @param n String name
		 * @param s float number of shares
		 * @param c float cost
		 * @param y float yield
		 */
		public Bond(String n, float s, float c, float y) {
			name = n;
			shares = s;
			cost = c;
			yield = y;
		}

		/** Default constructor */
		public Bond() {
		}

		/**
		 * Total cost function for each bond
		 * @return float total cost of bonds considered
		 */
		public float totalCost() {
			return shares * cost;
		}

		/**
		 * Total profit function for each bond
		 * @return float total profit of bonds considered
		 */
		public float totalProfit() {
			return shares * cost * yield;
		}

		/**
		 * Overrides toString method to list out information of Bond
		 * @return String with bond information
		 */
		public String toString() {
			return name + " Shares: " + shares + ", Cost per share: " + cost + ", Yield per share: " + yield;
		}

	}
	
	/**
	 * This class orders bonds from highest to lowest yield.
	 */
	static class HighestBondYieldComparator implements Comparator<Bond> {
		public int compare(Bond bond1, Bond bond2) {
			// your code here
			// if bond1 has higher yield, return -1 so it is before bond2
			if (bond1.yield > bond2.yield) {
				return -1;
			}
			// if bond1 has a lower yield, return 1 so it comes after bond2
			if (bond1.yield < bond2.yield) {
				return 1;
			}
			// if the yields are equal, return 0;
			return 0;
		}
	}

	/**
	 * Returns the optimum list of bonds from a bond priority queue.
	 * @param total total amount available to invest
	 * @param bonds collection of investment opportunities
	 * @return a portfolio of bonds
	 */
	static Collection<Bond> invest(float total, Collection<Bond> bonds) {
		// your code here

		PriorityQueue<Bond> bondPQ = new PriorityQueue<>(bonds.size(), new HighestBondYieldComparator());
		ArrayList<Bond> investments = new ArrayList<>(bonds.size()); //list to be returned
		float workingMoney = total;
		// add all bonds to the priority queue
		bondPQ.addAll(bonds);

		// loop through all elements of the priority queue
		while (!bondPQ.isEmpty()) {
			Bond workingBond = bondPQ.poll(); // remove the first bond each time
			if (workingBond.totalCost() <= workingMoney) { // check if whole bond can be added
				investments.add(workingBond);
				workingMoney -= workingBond.totalCost();
			} else if (workingMoney > 0){ // otherwise if you still have money, take a fraction bond.
				float sharesPossible = workingMoney / workingBond.cost;
				Bond partial = new Bond(workingBond.name, sharesPossible, workingBond.cost, workingBond.yield);
				investments.add(partial);
				workingMoney -= partial.totalCost();
			}
		}
		return investments;
	}
	
	/**
	 * Unit test class for investments.
	 */
	@FixMethodOrder(MethodSorters.NAME_ASCENDING)
	static public class TestInvestment {
		/**
		 * Total the bonds in a portfolio.
		 * @param bonds the collection of bonds
		 * @return to total cost of the bonds
		 */
		float totalCost(Collection<Bond> bonds) {
			float total = 0;
			for (Bond bond : bonds) {
				total += bond.totalCost();
			}
			return total;
		}
		
		/**
		 * Total profit of the bonds in a portfolio.
		 * @param bonds the collection of bonds
		 * @return to total profit of the bonds
		 */
		float totalProfit(Collection< Bond> bonds) {
			float total = 0;
			for (Bond bond : bonds) {
				total += bond.totalProfit();
			}
			return total;
		}
		/**
		 * Test purchasing all bonds with funds left over.
		 */
		@Test
		public void test_0010_tooMuchToInvest() {
			Bond[] bonds = {
			    new Bond("ACME", 50f, 10f, 0.060f),	
			    new Bond("MERC", 20f, 20f, 0.095f),	
			    new Bond("COKE", 100f, 30f, 0.020f)
			};
			Collection<Bond> investments = invest(4000f, Arrays.asList(bonds));
			
			assertEquals(3, investments.size());
			assertEquals(3900, totalCost(investments), 0f);
			assertEquals(128f, totalProfit(investments), 0.001f);
		}

		/**
		 * Test purchasing a whole positions.
		 */
		@Test
		public void test_0020_wholePositions() {
			
			Bond[] bonds = {
				    new Bond("ACME", 50f, 10f, 0.060f),	
				    new Bond("MERC", 20f, 20f, 0.095f),	
				    new Bond("COKE", 100f, 30f, 0.020f)
				};
			Collection<Bond> investments = invest(900f, Arrays.asList(bonds));

			assertEquals(2, investments.size());
			assertEquals(900f, totalCost(investments), 0.001f);
			assertEquals(68f, totalProfit(investments), 0.001f);
		}

		/**
		 * Test purchasing a fractional position.
		 */
		@Test
		public void test_0030_fractionalPositions() {
			
			Bond[] bonds = {
				    new Bond("ACME", 50f, 10f, 0.060f),	
				    new Bond("MERC", 20f, 20f, 0.095f),	
				    new Bond("COKE", 100f, 30f, 0.020f)
				};
			Collection<Bond> investments = invest(1000f, Arrays.asList(bonds));

			assertEquals(3, investments.size());
			
			// verify costs of individual items in the portfolio.
			for (Bond bond : investments) {
				if ("ACME".equals(bond.name)) {
					assertEquals(500f, bond.totalCost(), 0f);
				}
				if ("MERC".equals(bond.name)) {
					assertEquals(400f, bond.totalCost(), 0f);
				}
				if ("COKE".equals(bond.name)) {
					assertEquals(100f, bond.totalCost(), 0.01f);
				}
			}

			assertEquals(1000f, totalCost(investments), 0.001f);
			assertEquals(70f, totalProfit(investments), 0.001f);
		}

		/**
		 * Test purchasing with no money.
		 */
		@Test
		public void test_0040_noPositions() {

			Bond[] bonds = {
					new Bond("ACME", 50f, 10f, 0.060f),
					new Bond("MERC", 20f, 20f, 0.095f),
					new Bond("COKE", 100f, 30f, 0.020f)
			};
			Collection<Bond> investments = invest(0f, Arrays.asList(bonds));
			assertEquals(0, investments.size());
			assertEquals(0f, totalCost(investments), 0.001f);
			assertEquals(0f, totalProfit(investments), 0.001f);
		}
	}

	@Test

	/**
	 * Main program to drive unit tests.
	 * @param args unused
	 */
	public static void main(String[] args) {
		Result result = JUnitCore.runClasses(TestInvestment.class);

		System.out.println("[Unit Test Results]");
		System.out.println();

		if (result.getFailureCount() > 0) {
			System.out.println("Test failure details:");
			for (Failure failure : result.getFailures()) {
				System.out.println(failure.toString());
			}
			System.out.println();
		}

		int passCount = result.getRunCount() - result.getFailureCount() - result.getIgnoreCount();
		System.out.println("Test summary:");
		System.out.println("* Total tests = " + result.getRunCount());
		System.out.println("* Passed tests: " + passCount);
		System.out.println("* Failed tests = " + result.getFailureCount());
		System.out.println("* Inactive tests = " + result.getIgnoreCount());
	}
		
}

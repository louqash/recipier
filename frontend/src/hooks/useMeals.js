/**
 * Custom hook for fetching and managing meals data
 */
import { useState, useEffect } from 'react';
import { mealsAPI } from '../api/client';

export function useMeals(searchQuery = '') {
  const [meals, setMeals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [totalCount, setTotalCount] = useState(0);

  useEffect(() => {
    let isMounted = true;

    async function fetchMeals() {
      try {
        setLoading(true);
        setError(null);

        const data = await mealsAPI.getAll(searchQuery);

        if (isMounted) {
          setMeals(data.meals);
          setTotalCount(data.total_count);
        }
      } catch (err) {
        if (isMounted) {
          setError(err.message);
          console.error('Error fetching meals:', err);
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    }

    fetchMeals();

    // Cleanup function to prevent state updates on unmounted component
    return () => {
      isMounted = false;
    };
  }, [searchQuery]);

  /**
   * Refetch meals data
   */
  const refetch = () => {
    setLoading(true);
    mealsAPI.getAll(searchQuery)
      .then(data => {
        setMeals(data.meals);
        setTotalCount(data.total_count);
        setError(null);
      })
      .catch(err => {
        setError(err.message);
        console.error('Error refetching meals:', err);
      })
      .finally(() => {
        setLoading(false);
      });
  };

  return {
    meals,
    loading,
    error,
    totalCount,
    refetch,
  };
}

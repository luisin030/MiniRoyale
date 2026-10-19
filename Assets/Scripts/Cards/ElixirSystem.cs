using UnityEngine;
using System;

public class ElixirSystem : MonoBehaviour
{
    [SerializeField] private float maxElixir = 10f;
    [SerializeField] private float startingElixir = 5f;
    [SerializeField] private float elixirPerSecond = 0.5f;

    public float CurrentElixir { get; private set; }

    public event Action<float, float> OnElixirChanged;

    private void Start()
    {
        CurrentElixir = startingElixir;
        Notify();
    }

    private void Update()
    {
        if (GameManager.Instance != null && GameManager.Instance.MatchEnded)
            return;

        if (CurrentElixir < maxElixir)
        {
            CurrentElixir = Mathf.Min(maxElixir, CurrentElixir + elixirPerSecond * Time.deltaTime);
            Notify();
        }
    }

    public bool TrySpend(int amount)
    {
        if (CurrentElixir < amount)
            return false;

        CurrentElixir -= amount;
        Notify();
        return true;
    }

    private void Notify()
    {
        OnElixirChanged?.Invoke(CurrentElixir, maxElixir);
    }
}

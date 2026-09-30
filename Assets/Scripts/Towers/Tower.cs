using UnityEngine;

public class Tower : MonoBehaviour
{
    [SerializeField] private Team team = Team.Red;
    [SerializeField] private float maxHealth = 500f;

    public Team Team => team;
    public float CurrentHealth { get; private set; }

    private void Awake()
    {
        CurrentHealth = maxHealth;
    }

    public void TakeDamage(float damage)
    {
        CurrentHealth = Mathf.Max(0f, CurrentHealth - damage);
        Debug.Log($"{name}: {CurrentHealth}/{maxHealth}");

        if (CurrentHealth <= 0f)
            DestroyTower();
    }

    private void DestroyTower()
    {
        if (GameManager.Instance != null)
            GameManager.Instance.EndMatch(team);

        Destroy(gameObject);
    }
}

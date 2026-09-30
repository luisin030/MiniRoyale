using UnityEngine;

public class Unit : MonoBehaviour
{
    [SerializeField] private Team team = Team.Blue;
    [SerializeField] private float maxHealth = 100f;

    public Team Team => team;
    public float CurrentHealth { get; private set; }

    private void Awake()
    {
        CurrentHealth = maxHealth;
    }

    public void SetTeam(Team newTeam)
    {
        team = newTeam;
    }

    public void TakeDamage(float amount)
    {
        CurrentHealth -= amount;

        if (CurrentHealth <= 0f)
            Die();
    }

    private void Die()
    {
        Destroy(gameObject);
    }
}

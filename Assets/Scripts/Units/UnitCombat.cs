using UnityEngine;

[RequireComponent(typeof(UnitMovement))]
public class UnitCombat : MonoBehaviour
{
    [SerializeField] private float attackDamage = 20f;
    [SerializeField] private float attackRange = 1.3f;
    [SerializeField] private float attacksPerSecond = 1f;

    private UnitMovement movement;
    private float nextAttackTime;

    private void Awake()
    {
        movement = GetComponent<UnitMovement>();
    }

    private void Update()
    {
        if (GameManager.Instance != null && GameManager.Instance.MatchEnded)
            return;

        if (!movement.IsInRange(attackRange))
            return;

        if (Time.time < nextAttackTime)
            return;

        Attack();
        nextAttackTime = Time.time + 1f / attacksPerSecond;
    }

    private void Attack()
    {
        if (movement.Target == null)
            return;

        Tower tower = movement.Target.GetComponent<Tower>();

        if (tower != null)
        {
            tower.TakeDamage(attackDamage);
            Debug.Log($"{name} causou {attackDamage} de dano em {tower.name}");
        }
    }
}

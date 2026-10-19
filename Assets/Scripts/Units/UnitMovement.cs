using UnityEngine;

[RequireComponent(typeof(Unit))]
public class UnitMovement : MonoBehaviour
{
    [SerializeField] private float moveSpeed = 2f;
    [SerializeField] private float stopDistance = 1.2f;
    [SerializeField] private Transform target;

    private Unit unit;

    public Transform Target => target;

    private void Awake()
    {
        unit = GetComponent<Unit>();
    }

    private void Update()
    {
        if (GameManager.Instance != null && GameManager.Instance.MatchEnded)
            return;

        if (target == null)
            FindTarget();

        if (target == null)
            return;

        float distance = Vector2.Distance(transform.position, target.position);

        if (distance > stopDistance)
        {
            transform.position = Vector2.MoveTowards(
                transform.position,
                target.position,
                moveSpeed * Time.deltaTime
            );
        }
    }

    public bool IsInRange(float range)
    {
        return target != null &&
               Vector2.Distance(transform.position, target.position) <= range;
    }

    private void FindTarget()
    {
        Tower[] towers = FindObjectsByType<Tower>(FindObjectsSortMode.None);

        float bestDistance = float.MaxValue;
        Tower bestTarget = null;

        foreach (Tower tower in towers)
        {
            if (tower.Team == unit.Team)
                continue;

            float distance = Vector2.Distance(transform.position, tower.transform.position);

            if (distance < bestDistance)
            {
                bestDistance = distance;
                bestTarget = tower;
            }
        }

        if (bestTarget != null)
            target = bestTarget.transform;
    }
}

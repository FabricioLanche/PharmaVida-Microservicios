package com.example.farmacy.utils;

import jakarta.persistence.EntityManager;
import jakarta.persistence.PersistenceContext;
import jakarta.transaction.Transactional;
import org.springframework.stereotype.Component;

@Component
public class SequenceSyncUtil {

    @PersistenceContext
    private EntityManager entityManager;

    @Transactional
    public void syncSequence(String tableName, String idColumn) {
        try {
            Long maxId = ((Number) entityManager
                    .createNativeQuery("SELECT COALESCE(MAX(" + idColumn + "), 0) FROM " + tableName)
                    .getSingleResult()).longValue();

            long newSequenceValue = (maxId == 0) ? 1 : maxId;

            String seqQuery = String.format(
                    "SELECT setval(pg_get_serial_sequence('%s', '%s'), %d, %s)",
                    tableName, idColumn, newSequenceValue, (maxId != 0)
            );

            entityManager.createNativeQuery(seqQuery).getSingleResult();

            System.out.printf("✅ Secuencia sincronizada para %s (nuevo valor: %d)%n", tableName, newSequenceValue);
        } catch (Exception e) {
            System.err.printf("⚠️ Error al sincronizar secuencia para %s: %s%n", tableName, e.getMessage());
        }
    }
}

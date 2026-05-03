import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { getKnowledgeBases, saveKnowledgeBases } from '@/api/knowledge'
import { genId } from '@/utils/common'

export const useKnowledgeStore = defineStore('knowledge', () => {
  const bases = ref(getKnowledgeBases())
  const currentId = ref(bases.value[0]?.id || 'default')

  const currentBase = computed(() =>
    bases.value.find((b) => b.id === currentId.value) || bases.value[0]
  )

  function switchBase(id) {
    currentId.value = id
  }

  function addBase(name) {
    const base = { id: genId(), name, documents: [], createdAt: Date.now() }
    bases.value.push(base)
    saveKnowledgeBases(bases.value)
    return base
  }

  function removeBase(id) {
    if (id === 'default') return
    bases.value = bases.value.filter((b) => b.id !== id)
    if (currentId.value === id) currentId.value = bases.value[0]?.id || 'default'
    saveKnowledgeBases(bases.value)
  }

  function renameBase(id, name) {
    const base = bases.value.find((b) => b.id === id)
    if (base) {
      base.name = name
      saveKnowledgeBases(bases.value)
    }
  }

  function addDocument(baseId, doc) {
    const base = bases.value.find((b) => b.id === baseId)
    if (base) {
      base.documents.push(doc)
      saveKnowledgeBases(bases.value)
    }
  }

  function removeDocument(baseId, docId) {
    const base = bases.value.find((b) => b.id === baseId)
    if (base) {
      base.documents = base.documents.filter((d) => d.docId !== docId)
      saveKnowledgeBases(bases.value)
    }
  }

  return {
    bases, currentId, currentBase,
    switchBase, addBase, removeBase, renameBase,
    addDocument, removeDocument,
  }
})

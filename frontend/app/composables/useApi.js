
export const useApi = () => {
  const baseURL = 'http://localhost:8000/api'

  return {
   
    //resources
    fetchResources: () => $fetch(`${baseURL}/resources/get_resources`),
    createResource: (data) => $fetch(`${baseURL}/resources/create_resource`, { method: 'POST', body: data }),
    updateResource: (id, data) => $fetch(`${baseURL}/resources/update_resource/${id}`, { method: 'POST', body: data }),
    fetchResourceTypes : () => $fetch(`${baseURL}/resourceTypes/get_resourceTypes`),

    //disruptionTypes
    fetchDisruptionTypes: () => $fetch(`${baseURL}/disruptionTypes/get_disruptionTypes`),

    //disruptions
    fetchDisruptions: () => $fetch(`${baseURL}/disruptions/get_disruptions`),
    
    // Hilfsfunktion zum Speichern (POST für neu, PUT für edit)
    saveDisruption: (payload, id = null) => {
      const url = id 
        ? `${baseURL}/disruptions/update/${id}` // Beispiel für später
        : `${baseURL}/disruptions/create_disruption`
      
      return $fetch(url, {
        method: id ? 'PUT' : 'POST',
        body: payload
      })
    }
  }
}
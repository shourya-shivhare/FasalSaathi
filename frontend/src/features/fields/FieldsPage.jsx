import React, { useState } from 'react';
import { TopBar } from '../../components/layout/TopBar';
import { PageWrapper } from '../../components/layout/PageWrapper';
import { FieldCard } from './components/FieldCard';
import { AddFieldForm } from './components/AddFieldForm';
import { FieldMap } from './components/FieldMap';
import { Modal } from '../../components/ui/Modal';
import { Button } from '../../components/ui/Button';
import { Plus, Map } from 'lucide-react';
import { useFieldStore } from '../../stores/useFieldStore.jsx';

const FieldsPage = () => {
  const { fields, addField, setActiveField, activeFieldId } = useFieldStore();
  const [showAddForm, setShowAddForm] = useState(false);
  const [showFieldMap, setShowFieldMap] = useState(false);
  const [selectedField, setSelectedField] = useState(null);

  const handleAddField = async (fieldData) => {
    const newField = addField(fieldData);
    setShowAddForm(false);
    setActiveField(newField.id);
  };

  const handleViewDetails = (field) => {
    setSelectedField(field);
    setShowFieldMap(true);
    setActiveField(field.id);
  };

  const handleLocationUpdate = (coords) => {
    console.log('Location updated:', coords);
    // In a real app, this would update the field's location
  };

  return (
    <PageWrapper>
      <TopBar
        icon={Map}
        title="My Fields"
        subtitle={`${fields.length} field${fields.length !== 1 ? 's' : ''}`}
        rightAction={
          <Button
            variant="primary"
            size="sm"
            icon={Plus}
            onClick={() => setShowAddForm(true)}
          >
            Add Field
          </Button>
        }
      />

      <div className="p-4 space-y-4">
        {fields.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-6xl mb-4">🌾</div>
            <h3 className="text-lg font-semibold text-stone-900 mb-2">
              No fields added yet
            </h3>
            <p className="text-stone-600 mb-6">
              Add your first field to start tracking your farm's health and progress
            </p>
            <Button
              variant="primary"
              icon={Plus}
              onClick={() => setShowAddForm(true)}
            >
              Add Your First Field
            </Button>
          </div>
        ) : (
          <div className="space-y-4">
            {fields.map((field) => (
              <FieldCard
                key={field.id}
                field={field}
                onViewDetails={handleViewDetails}
                isActive={field.id === activeFieldId}
              />
            ))}
          </div>
        )}
      </div>

      {/* Add Field Modal */}
      <Modal
        isOpen={showAddForm}
        onClose={() => setShowAddForm(false)}
        size="lg"
      >
        <AddFieldForm
          onSubmit={handleAddField}
          onCancel={() => setShowAddForm(false)}
        />
      </Modal>

      {/* Field Map Modal */}
      <Modal
        isOpen={showFieldMap}
        onClose={() => setShowFieldMap(false)}
        title={selectedField ? `${selectedField.name} - Map View` : 'Field Map'}
        size="xl"
      >
        {selectedField && (
          <FieldMap
            field={selectedField}
            onLocationUpdate={handleLocationUpdate}
          />
        )}
      </Modal>
    </PageWrapper>
  );
};

export { FieldsPage };

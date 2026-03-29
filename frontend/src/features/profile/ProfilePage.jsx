import React, { useState } from 'react';
import { User, Plus, MapPin, Phone } from 'lucide-react';
import { TopBar } from '../../components/layout/TopBar';
import { PageWrapper } from '../../components/layout/PageWrapper';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Modal } from '../../components/ui/Modal';
import { useUserStore } from '../../stores/useUserStore.jsx';
import { useFieldStore } from '../../stores/useFieldStore.jsx';
import { AddFieldForm } from '../fields/components/AddFieldForm';
import { FieldCard } from '../fields/components/FieldCard';
import { FieldMap } from '../fields/components/FieldMap';

const ProfilePage = () => {
  const { farmer } = useUserStore();
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
  };

  return (
    <PageWrapper>
      <TopBar
        icon={User}
        title="My Profile"
        subtitle="Manage your farming details"
      />

      <div className="p-4 space-y-6 pb-24">
        {/* User Card */}
        <Card className="theme-bg-secondary border theme-border overflow-hidden">
          <div className="flex items-center gap-4 mb-4">
            <div className="w-16 h-16 rounded-full theme-bg-accent-primary flex items-center justify-center shadow-lg">
              <span className="text-2xl font-bold text-white">
                {farmer?.name?.charAt(0) || 'F'}
              </span>
            </div>
            <div>
              <h2 className="text-xl font-bold theme-text-primary">{farmer?.name || 'Farmer'}</h2>
              <p className="text-sm theme-text-secondary flex items-center gap-1 mt-1">
                <MapPin className="w-3.5 h-3.5" />
                {farmer?.location || 'Location Not Set'}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2 text-sm theme-text-primary bg-black/5 dark:bg-white/5 p-3 rounded-xl">
            <Phone className="w-4 h-4 theme-text-secondary" />
            {farmer?.phone || '+91 XXXXX XXXXX'}
          </div>
        </Card>

        {/* Crops & Fields Section */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-bold theme-text-primary text-lg">My Sown Fields</h3>
            <Button
              variant="outline"
              size="sm"
              icon={Plus}
              onClick={() => setShowAddForm(true)}
              className="text-xs"
            >
              Add New
            </Button>
          </div>

          {fields.length === 0 ? (
            <div className="text-center py-10 bg-black/5 dark:bg-white/5 rounded-2xl border border-dashed theme-border">
              <div className="text-4xl mb-3">🌾</div>
              <h3 className="theme-text-primary font-semibold">No crop fields added</h3>
              <p className="text-xs theme-text-secondary mt-1 max-w-[200px] mx-auto">
                Add fields to get personalized advisory and crop health updates.
              </p>
              <Button
                variant="primary"
                size="sm"
                icon={Plus}
                onClick={() => setShowAddForm(true)}
                className="mt-4"
              >
                Add Field Details
              </Button>
            </div>
          ) : (
            <div className="grid gap-4">
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
        title={selectedField ? `${selectedField.name}` : 'Field Details'}
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

export { ProfilePage };
